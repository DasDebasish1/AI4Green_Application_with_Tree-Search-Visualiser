""" Module containing a class that is the main interface the retrosynthesis tool.
"""
from __future__ import annotations
import time
from collections import defaultdict
from typing import TYPE_CHECKING
from multiprocessing import Process, Queue
import importlib

from tqdm import tqdm
from copy import deepcopy
# This must be imported first to setup logging for rdkit, tensorflow etc
from aizynthfinder.utils.logging import logger
from aizynthfinder.utils.loading import load_dynamic_class
from aizynthfinder.context.config import Configuration,ModifiedConfiguration
from aizynthfinder.search.mcts import MctsSearchTree
from aizynthfinder.reactiontree import ReactionTreeFromExpansion
from aizynthfinder.analysis import (
    TreeAnalysis,
    RouteCollection,
    RouteSelectionArguments,
)
from aizynthfinder.chem import Molecule, TreeMolecule, FixedRetroReaction
from aizynthfinder.search.andor_trees import AndOrSearchTreeBase
from aizynthfinder.utils.exceptions import MoleculeException

if TYPE_CHECKING:
    from aizynthfinder.utils.type_utils import (
        StrDict,
        Optional,
        Union,
        Callable,
        List,
        Tuple,
        Dict,
    )
    from aizynthfinder.chem import RetroReaction



def worker(id,smiles,iterations, configfile=None,config_dict=None,stock=None):
        st = time.time()
        if configfile:
            config = ModifiedConfiguration.from_file(configfile)
        elif config_dict:
            config = ModifiedConfiguration.from_dict(config_dict)
        config.stock=stock
        print(time.time()-st,1)
        st = time.time()

        expansion_policy = config.expansion_policy
        filter_policy = config.filter_policy
        stock = config.stock
        scorers = config.scorers
        stocks = list([])
        try:
            module = importlib.import_module("custom_stock")
        except ModuleNotFoundError:
            pass
        else:
            if hasattr(module, "stock"):
                stock.load(module.stock, "custom_stock")  # type: ignore
                stocks.append("custom_stock")
        print(time.time()-st,2)
        st = time.time()
        
        stock.select(stocks or stock.items)
        config.expansion_policy.select("full_uspto")
        tartget_mole=Molecule(smiles=smiles)
        print(time.time()-st,3)
        st = time.time()
        
        tartget_mole.sanitize()
        print(tartget_mole.smiles)
        stock.reset_exclusion_list()
        if config.exclude_target_from_stock and tartget_mole in stock:
            stock.exclude(tartget_mole)
        tree= MctsSearchTree(root_smiles=smiles, config=config)
        routes =RouteCollection([])
        search_stats = {"returned_first": False, "iterations": 0}
        print(time.time()-st,4)
        

        time0 = time.time()
        i = 1
        
        time_past = time.time() - time0
        tree.root.totaliterations=iterations
        for iii in range(iterations):
            search_stats["iterations"] += 1
            try:
                is_solved = tree.one_iteration()
                # print(self.config.current_iteration)
                print(i)
                
            except StopIteration:
                break
            
            if is_solved and "first_solution_time" not in search_stats:
                search_stats["first_solution_time"] = time.time() - time0
                search_stats["first_solution_iteration"] = i

            if config.return_first and is_solved:
                search_stats["returned_first"] = True
                break
            
            
            i += 1
            time_past = time.time() - time0
            
            
        time_past = time.time() - time0
        search_stats["time"] = time_past
        
        #search_stats["tree"] = tree
        # queue.put(search_stats)
      
        analysis = TreeAnalysis(tree, scorer=scorers["state score"])
        config_selection = RouteSelectionArguments(
            nmin=config.post_processing.min_routes,
            nmax=config.post_processing.max_routes,
            return_all=config.post_processing.all_routes,
        )
        
        routes = RouteCollection.from_analysis(
            analysis,  config_selection
        )
        routes.compute_scores(*scorers.objects())
        
        stats = {
            "target": smiles,
            "search_time": search_stats["time"],
            "first_solution_time": search_stats.get("first_solution_time", 0),
            "first_solution_iteration": search_stats.get(
                "first_solution_iteration", 0
            ),
        }
        stats.update(analysis.tree_statistics())
        best=analysis.best()
        tree.serialize(f"{id}.json")
        with open(f"{id}_score.txt","w") as file:
            file.write(str(stats["number_of_solved_routes"]))


class AiZynthFinder:
    """
    Public API to the aizynthfinder tool

    If instantiated with the path to a yaml file or dictionary of settings
    the stocks and policy networks are loaded directly.
    Otherwise, the user is responsible for loading them prior to
    executing the tree search.

    :ivar config: the configuration of the search
    :ivar expansion_policy: the expansion policy model
    :ivar filter_policy: the filter policy model
    :ivar stock: the stock
    :ivar scorers: the loaded scores
    :ivar tree: the search tree
    :ivar analysis: the tree analysis
    :ivar routes: the top-ranked routes
    :ivar search_stats: statistics of the latest search

    :param configfile: the path to yaml file with configuration (has priority over configdict), defaults to None
    :param configdict: the config as a dictionary source, defaults to None
    """

    def __init__(self, configfile: str = None, configdict: StrDict = None) -> None:
        self._logger = logger()
        self.config_dict = None
        self.configfile = None

        if configfile:
            self.config = Configuration.from_file(configfile)
            self.configfile = configfile

        elif configdict:
            self.config = Configuration.from_dict(configdict)
            self.config_dict = configdict

        else:
            self.config = Configuration()

        self.expansion_policy = self.config.expansion_policy
        self.filter_policy = self.config.filter_policy
        self.stock = self.config.stock
        self.scorers = self.config.scorers
        self.tree: Optional[Union[MctsSearchTree, AndOrSearchTreeBase]] = None
        self._target_mol: Optional[Molecule] = None
        self.search_stats: StrDict = dict()
        self.routes = RouteCollection([])
        self.analysis: Optional[TreeAnalysis] = None

    @property
    def target_smiles(self) -> str:
        """The SMILES representation of the molecule to predict routes on."""
        if not self._target_mol:
            return ""
        return self._target_mol.smiles

    @target_smiles.setter
    def target_smiles(self, smiles: str) -> None:
        self.target_mol = Molecule(smiles=smiles)

    @property
    def target_mol(self) -> Optional[Molecule]:
        """The molecule to predict routes on"""
        return self._target_mol

    @target_mol.setter
    def target_mol(self, mol: Molecule) -> None:
        self.tree = None
        self._target_mol = mol

    def build_routes(
        self, selection: RouteSelectionArguments = None, scorer: str = "state score"
    ) -> None:
        """
        Build reaction routes

        This is necessary to call after the tree search has completed in order
        to extract results from the tree search.

        :param selection: the selection criteria for the routes
        :param scorer: a reference to the object used to score the nodes
        :raises ValueError: if the search tree not initialized
        """
        if not self.tree:
            raise ValueError("Search tree not initialized")

        self.analysis = TreeAnalysis(self.tree, scorer=self.scorers[scorer])
        config_selection = RouteSelectionArguments(
            nmin=self.config.post_processing.min_routes,
            nmax=self.config.post_processing.max_routes,
            return_all=self.config.post_processing.all_routes,
        )
        self.routes = RouteCollection.from_analysis(
            self.analysis, selection or config_selection
        )

    def extract_statistics(self) -> StrDict:
        """Extracts tree statistics as a dictionary"""
        if not self.analysis:
            return {}
        stats = {
            "target": self.target_smiles,
            "search_time": self.search_stats["time"],
            "first_solution_time": self.search_stats.get("first_solution_time", 0),
            "first_solution_iteration": self.search_stats.get(
                "first_solution_iteration", 0
            ),
        }
        stats.update(self.analysis.tree_statistics())
        return stats

    def prepare_tree(self) -> None:
        """
        Setup the tree for searching

        :raises ValueError: if the target molecule was not set
        """
        if not self.target_mol:
            raise ValueError("No target molecule set")

        try:
            self.target_mol.sanitize()
        except MoleculeException:
            raise ValueError("Target molecule unsanitizable")

        self.stock.reset_exclusion_list()
        if self.config.exclude_target_from_stock and self.target_mol in self.stock:
            self.stock.exclude(self.target_mol)
            self._logger.debug("Excluding the target compound from the stock")

        self._setup_search_tree()
        self.analysis = None
        self.routes = RouteCollection([])

    def stock_info(self) -> StrDict:
        """
        Return the stock availability for all leaf nodes in all collected reaction trees

        The key of the return dictionary will be the SMILES string of the leaves,
        and the value will be the stock availability

        :return: the collected stock information.
        """
        if not self.analysis:
            return {}
        _stock_info = {}
        for tree in self.routes.reaction_trees:
            for leaf in tree.leafs():
                if leaf.smiles not in _stock_info:
                    _stock_info[leaf.smiles] = self.stock.availability_list(leaf)
        return _stock_info

    def tree_search11(self, show_progress: bool = False) -> float:
        """
        Perform the actual tree search

        :param show_progress: if True, shows a progress bar
        :return: the time past in seconds
        """
        if not self.tree:
            self.prepare_tree()
        # This is for type checking, prepare_tree is creating it.
        assert self.tree is not None
        self.search_stats = {"returned_first": False, "iterations": 0}

        time0 = time.time()
        i = 1
        self._logger.debug("Starting search")
        time_past = time.time() - time0

        if show_progress:
            pbar = tqdm(total=self.config.iteration_limit, leave=False)

        while time_past < self.config.time_limit and i <= self.config.iteration_limit:
            if show_progress:
                pbar.update(1)
            self.search_stats["iterations"] += 1

            try:
                is_solved = self.tree.one_iteration()
            except StopIteration:
                break

            if is_solved and "first_solution_time" not in self.search_stats:
                self.search_stats["first_solution_time"] = time.time() - time0
                self.search_stats["first_solution_iteration"] = i

            if self.config.return_first and is_solved:
                self._logger.debug("Found first solved route")
                self.search_stats["returned_first"] = True
                break
            i = i + 1
            time_past = time.time() - time0

        if show_progress:
            pbar.close()
        time_past = time.time() - time0
        self._logger.debug("Search completed")
        self.search_stats["time"] = time_past
        return time_past
    def tree_search(self, show_progress: bool = False,iterations=100) -> float:
        self.trees=[]
        # if not self.tree:
        #     self.prepare_tree()
        # assert self.tree is not None
        self.search_stats = {"returned_first": False, "iterations": 0}
        time0 = time.time()
        self._logger.debug("Starting search")
        time_past = time.time() - time0
        if show_progress:
            pbar = tqdm(total=self.config.iteration_limit, leave=False)
        n_processes=1
        stock=deepcopy(self.config.stock)
        processes = [Process(target=worker, args=( x,self.target_smiles,iterations,self.configfile,self.config_dict,stock)) for x in range(n_processes)]
        with open("num_process.txt","w") as f:
            f.write(str(n_processes))
        # Run processes
        for p in processes:
            p.start()

        # Exit the completed processes
        for p in processes:
            p.join()
 
       
        MAX_SCORE=0
        SELECT_TREE=0

        for ti in range(n_processes):
            with open(f"{ti}_score.txt","r") as f:
                sc=int(f.read())
                if MAX_SCORE<sc:
                    MAX_SCORE=sc
                    SELECT_TREE=ti
        self.tree = MctsSearchTree.from_json(f"{SELECT_TREE}.json",self.config)
        self.tree.root.totaliterations=iterations
        if show_progress:
            pbar.close()
        time_past = time.time() - time0
        self.search_stats["time"] = time_past
        
        self._logger.debug("Search completed")
        
        return time_past
    def _setup_search_tree(self):
        self._logger.debug("Defining tree root: %s" % self.target_smiles)
        if self.config.search_algorithm.lower() == "mcts":
            self.tree = MctsSearchTree(
                root_smiles=self.target_smiles, config=self.config
            )
        else:
            cls = load_dynamic_class(self.config.search_algorithm)
            self.tree: AndOrSearchTreeBase = cls(
                root_smiles=self.target_smiles, config=self.config
            )


class AiZynthExpander:
    """
    Public API to the AiZynthFinder expansion and filter policies

    If instantiated with the path to a yaml file or dictionary of settings
    the stocks and policy networks are loaded directly.
    Otherwise, the user is responsible for loading them prior to
    executing the tree search.

    :ivar config: the configuration of the search
    :ivar expansion_policy: the expansion policy model
    :ivar filter_policy: the filter policy model

    :param configfile: the path to yaml file with configuration (has priority over configdict), defaults to None
    :param configdict: the config as a dictionary source, defaults to None
    """

    def __init__(self, configfile: str = None, configdict: StrDict = None) -> None:
        self._logger = logger()

        if configfile:
            self.config = Configuration.from_file(configfile)
        elif configdict:
            self.config = Configuration.from_dict(configdict)
        else:
            self.config = Configuration()

        self.expansion_policy = self.config.expansion_policy
        self.filter_policy = self.config.filter_policy
        self.stats: StrDict = {}

    def do_expansion(
        self,
        smiles: str,
        return_n: int = 5,
        filter_func: Callable[[RetroReaction], bool] = None,
    ) -> List[Tuple[FixedRetroReaction, ...]]:
        """
        Do the expansion of the given molecule returning a list of
        reaction tuples. Each tuple in the list contains reactions
        producing the same reactants. Hence, nested structure of the
        return value is way to group reactions.

        If filter policy is setup, the probability of the reactions are
        added as metadata to the reaction.

        The additional filter functions makes it possible to do customized
        filtering. The callable should take as only argument a `RetroReaction`
        object and return True if the reaction can be kept or False if it should
        be removed.

        :param smiles: the SMILES string of the target molecule
        :param return_n: the length of the return list
        :param filter_func: an additional filter function
        :return: the grouped reactions
        """
        self.stats = {"non-applicable": 0}

        mol = TreeMolecule(parent=None, smiles=smiles)
        actions, _ = self.expansion_policy.get_actions([mol])
        results: Dict[Tuple[str, ...], List[FixedRetroReaction]] = defaultdict(list)
        for action in actions:
            reactants = action.reactants
            if not reactants:
                self.stats["non-applicable"] += 1
                continue
            if filter_func and not filter_func(action):
                continue
            for name in self.filter_policy.selection or []:
                if hasattr(self.filter_policy[name], "feasibility"):
                    _, feasibility_prob = self.filter_policy[name].feasibility(action)
                    action.metadata["feasibility"] = float(feasibility_prob)
                    break
            action.metadata["expansion_rank"] = len(results) + 1
            unique_key = tuple(sorted(mol.inchi_key for mol in reactants[0]))
            if unique_key not in results and len(results) >= return_n:
                continue
            rxn = next(ReactionTreeFromExpansion(action).tree.reactions())  # type: ignore
            results[unique_key].append(rxn)
        return [tuple(reactions) for reactions in results.values()]
