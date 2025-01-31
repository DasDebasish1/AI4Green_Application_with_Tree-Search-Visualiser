import itertools
from typing import List, Tuple

import pandas as pd
from sources import services

"""
File containing functions and classes that get data on compounds
and interconvert between different molecular representations
"""


def get_compound_data(compound_smiles: str) -> Tuple[List, List, List, List]:
    """
    Takes the list of smiles and type of compound to look up the compounds in the database and return data on them.

    Args:
        compound_smiles - '.' delimited string of the SMILES of each compound of a particular type (e.g., reactants)

    Returns:
        A tuple containing lists of:
        - SMILES for each compound
        - Compound objects or "No Compound" if not found
        - Names of each compound or "No Compound" if not found
        - IDs of each compound or "No Compound" if not found
    """
    smiles_list = smiles_str_to_list(compound_smiles)
    compound_data = {"smiles": [], "compound_object": [], "name": [], "id": []}
    for smiles in smiles_list:
        compound_object = services.compound.get_compound_from_smiles(smiles)
        compound_data["smiles"].append(smiles)
        if compound_object:
            compound_data["compound_object"].append(compound_object)
            compound_data["name"].append(compound_object.name)
            compound_data["id"].append(compound_object.id)
        else:
            compound_data["compound_object"].append("No Compound")
            compound_data["name"].append("No Compound")
            compound_data["id"].append("No Compound")

    return (
        compound_data["smiles"],
        compound_data["compound_object"],
        compound_data["name"],
        compound_data["id"],
    )
    # return smiles_list, compound_list, name_list, id_list


def smiles_str_to_list(compound_smiles: str) -> List[str]:
    """
    Takes the smiles string with '.' delimiter and makes a list. Checking for ions and handling them

    Args:
        compound_smiles (str): The SMILES string with '.' delimiter.

    Returns:
        A list of SMILES strings, processed to handle ions if present.
    """

    if ion_check(compound_smiles):
        # function to process ions then convert to list, eg na+.oh-.cco > [na.oh, cco]
        smiles_list = IonicCompounds(compound_smiles).get_smiles_list()
    else:
        smiles_list = compound_smiles.split(".")
    return smiles_list


class IonicCompounds:
    """
    Class to process ions in a smiles string. Tries to combine ions into an ionic compound. e.g., Na+ Cl- -> NaCl
    """

    def __init__(self, delimited_smiles: str):
        """
        Args:
            delimited_smiles: smiles with a '.' delimiter
        """

        self.smiles_string = delimited_smiles
        self.smiles_list = delimited_smiles.split(".")
        self.possible_ionic_compound_list = []
        self.ionic_compound_eval_list = []  # list of dicts
        self.ions_to_keep = []
        self.processed_smiles_list = []

    def get_smiles_list(self) -> List[str]:
        """
        Process ions in the smiles string.

        Returns:
            list: Processed smiles list.
        """
        self.make_ions_compounds()
        self.evaluate_ionic_compounds()
        self.select_best_ion_compounds()
        self.format_smiles_list()
        return self.processed_smiles_list

    def make_ions_compounds(self):
        """
        Make ionic compounds using itertools.
        """
        self.possible_ionic_compound_list = []
        for i in range(1, len(self.smiles_list) + 1):
            combinations = [
                y
                for y in [
                    x for x in itertools.combinations(enumerate(self.smiles_list), i)
                ]
            ]
            dic_ls = [{"idx": x[0], "ion": x[1]} for x in combinations[0]]
            ionic_compound = ""
            idx_ls = []
            for idx, dic in enumerate(dic_ls):
                ionic_compound += dic["ion"]
                idx_ls.append(dic["idx"])
            if "+" in ionic_compound or "-" in ionic_compound:
                new_dic = {"idx_list": idx_ls, "ionic_compound": ionic_compound}
                self.possible_ionic_compound_list.append(new_dic)

    def evaluate_ionic_compounds(self):
        """
        Evaluate ionic compounds. H is likely to exist and L unlikely
        """
        for ionic_compound_dict in self.possible_ionic_compound_list:
            ion_smiles = ionic_compound_dict["ionic_compound"]
            compound_object = services.compound.get_compound_from_smiles(ion_smiles)
            balanced_charge = self.charges_balanced(ion_smiles)
            if compound_object and balanced_charge:
                ionic_compound_dict.update({"eval": "H"})
            elif compound_object:
                ionic_compound_dict.update({"eval": "M"})
            elif balanced_charge:
                ionic_compound_dict.update({"eval": "L"})
            else:
                ionic_compound_dict.update({"eval": "VL"})
            self.ionic_compound_eval_list.append(ionic_compound_dict)

    def select_best_ion_compounds(self):
        """
        Select the best ion compounds.
        """
        df = pd.DataFrame(self.ionic_compound_eval_list)
        score_list = ["H", "M", "L", "VL"]
        for score in score_list:
            best_ion = df[df["eval"] == score]
            if not best_ion.empty:
                self.ions_to_keep.append(best_ion.to_dict(orient="records")[0])
                break

    def format_smiles_list(self):
        """
        Format the smiles list.
        """
        ions_in_previous_salts = 0
        self.processed_smiles_list = self.smiles_list
        for ion_dict in self.ions_to_keep:
            ion_indexes = ion_dict["idx_list"]
            insert_index = ion_indexes[0] - ions_in_previous_salts
            end_index = insert_index + len(ion_indexes)
            del self.processed_smiles_list[insert_index:end_index]
            self.processed_smiles_list.insert(insert_index, ion_dict["ionic_compound"])

    @staticmethod
    def charges_balanced(ion_string: str) -> bool:
        """
        Check if charges are balanced in the ion string.

        Returns:
            bool: True if charges are balanced, False otherwise.
        """
        positive_charges = ion_string.count("+")
        negative_charges = ion_string.count("-")
        if positive_charges == negative_charges:
            return True
        return False


def ion_check(smiles: str) -> bool:
    if any(x in smiles for x in ["+", "-"]):
        return True
    return False
