import json
from typing import Dict, List, Tuple

import requests
from flask import current_app
import urllib.parse

from .compounds import get_compound_data
from .utils import encodings_to_smiles_symbols, sig_figs_on_numbers


def get_reaction_condition(reaction_smiles):
    base_url = current_app.config["CONDITIONS_API_URL"]
    api_key = current_app.config["CONDITIONS_API_KEY"]
    #f={"key":api_key,"smiles":reaction_smiles}
    
    #request_url = f"{base_url}/condition_prediction_api/?"+urllib.parse.urlencode(f)
    #print(request_url)
    request_url = f"{base_url}/condition_prediction_api/?key={api_key}&smiles={reaction_smiles}"
    
    try:
        response = requests.get(request_url)
        return json.loads(response.content)["Message"]
        
    except Exception:
       pass

def get_conditions(solved_routes: dict) -> List[dict]:
    """
    Takes the retrosynthetic routes and send an api call with the reaction smiles
    to get conditions for each forward reaction.

    Args:
        solved_routes - retrosynthetic routes
        conditions_api_key - key required to access the conditions api
        conditions_base_url - the url to access the conditions api

    Returns:
        List of conditions with a dictionary for each route.

    """
    conditions_results = []
    for (
        route_label,
        route,
    ) in solved_routes.items():
        conditions_results.append(
            RouteConditions(route_label, route).get_route_conditions()
        )
    return conditions_results


class RouteConditions:
    """
    Class to handle conditions for a specific route.
    """

    base_url = current_app.config["CONDITIONS_API_URL"]
    api_key = current_app.config["CONDITIONS_API_KEY"]

    def __init__(self, route_label, route):
        self.route_label = route_label
        self.route = route

    def get_route_conditions(self) -> Dict:
        """
        Get conditions for each step in the route.

        Returns:
            dict: Conditions for the route.
        """
        route_conditions = []
        for idx, node in enumerate(self.route["steps"]):
            child_smiles = node.get("child_smiles")
            # child smiles are the reactants. if there are none it is a terminal node.
            if child_smiles:
                # get the conditions or make note of the failed api call
                api_status, reaction_conditions = ReactionConditions(
                    child_smiles, node["smiles"], self
                ).get_reaction_conditions()
                if api_status["status"] == "failed":
                    reaction_conditions = "Condition Prediction Unsuccessful"
                # add the results to the dictionary and list
                reaction_conditions_dict = {node["node_id"]: reaction_conditions}
                route_conditions.append(reaction_conditions_dict)
        return {self.route_label: route_conditions}


class ReactionConditions(RouteConditions):
    """
    Class to handle conditions for a specific reaction.
    """

    def __init__(self, reactants_smiles, product_smiles, route_conditions):
        super().__init__(route_conditions.base_url, route_conditions.api_key)
        self.reactants_smiles = reactants_smiles
        self.product_smiles = product_smiles
        self.reaction_smiles = encodings_to_smiles_symbols(
            ".".join(self.reactants_smiles) + ">>" + self.product_smiles
        )
        self.response = ""
        self.predicted_conditions = []
        self.api_status = {}

    def get_reaction_conditions(self) -> Tuple[Dict, List]:
        """
        Gets conditions for a specific reaction

        Returns
            dict - the api status success or fail and why if failure
            list of dicts - predicted conditions

        """
        self.api_call()
        self.validate_conditions_api_response()
        processed_conditions = ProcessConditions(
            self.predicted_conditions, self.reaction_smiles, self.product_smiles
        ).process_conditions()
        return self.api_status, processed_conditions

    def api_call(self):
        """
        Makes the api call to the condition prediction url to get the conditions data
        """

        request_url = f"{self.base_url}/condition_prediction_api/?key={self.api_key}&smiles={self.reaction_smiles}"
        try:
            self.response = requests.get(request_url)
            self.predicted_conditions = json.loads(self.response.content)["Message"]
           
        except Exception:
            failure_message = self.determine_conditions_api_error()
            self.exit("failed", failure_message, "")

    def validate_conditions_api_response(self):
        """
        Looks for potential failures in api response and creates the appropriate message to detail error to user
        """
        # if the response is valid check whether conditions were successfully found
        if self.response.status_code == 200:
            if self.predicted_conditions == "invalid key":
                self.api_status = {"status": "failed", "message": "Invalid key"}
            if self.predicted_conditions:
                self.api_status = {
                    "status": "success",
                    "message": "Conditions successfully found for reaction",
                }
            else:
                self.api_status = {
                    "status": "failed",
                    "message": "No conditions found for reaction",
                }
        # if response was not valid, check the reasons for this
        elif self.response.status_code == 401:
            self.api_status = {"status": "failed", "message": "Invalid key"}
        else:
            self.api_status = {
                "status": "failed",
                "message": "Conditions API responded with error code: "
                + self.response.status_code
                + "If this is a repeated error please report "
                "this to admin@ai4green.app, with details of your error",
            }

    def determine_conditions_api_error(self) -> str:
        """
        In the event of no response from or no 'Message' key in the JSON response from the conditions API.
        We call to the API to see if the server is running
        """
        url = f"{self.base_url}/"
        try:
            response = requests.get(url)
            response_content = json.loads(response.content["Message"])
        except Exception:
            return "Conditions Prediction server is down. If this problem persists you can report to admin@ai4green.app"
        if not response_content == "Conditions service is running":
            return (
                "Conditions Prediction service is currently having technical issues. If this problem persists you can report "
                "to admin@ai4green.app"
            )
        return "Error getting conditions. You can report this problem to admin@ai4green.app"

    @staticmethod
    def exit(api_status: str, message: str, conditions: str):
        return api_status, message, conditions


class ProcessConditions:
    """
    A Class to process conditions got from the api request into a list.
    Processing includes looking up compounds in the database to get additional data and rounding numbers.
    """

    def __init__(
        self, predicted_conditions: List, reactants_smiles: str, product_smiles: str
    ):
        self.predicted_conditions = predicted_conditions
        self.reactants_smiles = reactants_smiles
        self.product_smiles = product_smiles

    def process_conditions(self):
        """Constructs a list of dictionaries with keys for the Names and Database IDS of:
        solvents, reagent, catalyst, reactants, and products, with the properties as a list
        """
        compound_keys = ["solvent", "reagents", "catalyst", "reactant", "product"]
        for condition_set in self.predicted_conditions:
            # add all keys to the condition_set dict, so it has name/id keys for all compound types.
            self.add_compound_to_dict(self.reactants_smiles, condition_set, "reactant")
            self.add_compound_to_dict(self.product_smiles, condition_set, "product")
            self.add_name_keys_to_dict(condition_set, compound_keys)
            for compound_type, compound_smiles in condition_set.items():
                # skips non-compound keys in condition set
                if compound_type not in compound_keys:
                    continue
                # get list of smiles then compounds, then save name and ids to the dictionary
                smiles_list, compound_list, name_list, id_list = get_compound_data(
                    compound_smiles
                )
                #
                # smiles_list = self.smiles_str_to_list(compound_smiles)
                # compound_list = self.smiles_list_to_compounds(smiles_list)
                # name_list = self.get_compound_name_list(compound_list, compound_type)
                # id_list = self.get_compound_id_list(compound_list, compound_type)
                self.update_conditions_dict(
                    name_list, id_list, smiles_list, condition_set, compound_type
                )
                sig_figs_on_numbers(condition_set)
        return self.predicted_conditions

    @staticmethod
    def add_compound_to_dict(smiles: str, condition_set: Dict, compound_type: str):
        """Adds smiles as a string delimited by '.'"""
        if type(smiles) is str:
            condition_set[compound_type] = smiles
        elif type(smiles) is list:
            try:
                condition_set[compound_type] = ".".join(smiles)
            except Exception as e:
                print(e)
        else:
            print("unexpected type")

    @staticmethod
    def add_name_keys_to_dict(condition_set: dict, compound_keys: List[str]):
        """Updates the dictionary"""
        for key in compound_keys:
            condition_set[f"{key}_names"] = ""
            condition_set[f"{key}_ids"] = ""
            condition_set[f"{key}_smiles"] = ""

    @staticmethod
    def update_conditions_dict(
        name_list: List[str],
        id_list: List[int],
        smiles_list: List[str],
        condition_set: Dict,
        compound_type: str,
    ):
        # add name and id for each compound
        condition_set[f"{compound_type}_names"] = name_list
        condition_set[f"{compound_type}_ids"] = id_list
        condition_set[f"{compound_type}_smiles"] = smiles_list
