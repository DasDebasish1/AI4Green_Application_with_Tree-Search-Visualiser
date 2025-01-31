import json
from typing import Dict, List, Tuple, Union

import requests

from .utils import sig_figs_on_numbers


def retrosynthesis_api_call(
    request_url: str, retrosynthesis_base_url: str
) -> Tuple[str, str, Union[str, List[Dict]]]:
    print("request made to", request_url)
    try:
        response = requests.get(request_url)
        resp = json.loads(response.content)

        solved_routes = resp["Message"]
        Tree= resp["Tree"]
        if solved_routes == "invalid key":
            return "failed", "invalid key", "",""
        if solved_routes == {}:
            return "failed", "Could not find a successful route to the molecule.", "",Tree
        assert solved_routes
        # if query fails try and print error code but
    except Exception:
        failure_message = determine_retrosynthesis_error(retrosynthesis_base_url)
        return "failed", failure_message, "",""
    # if query successful then validate
    print("successful query")
    validation, validation_message = validate_retrosynthesis_api_response(
        response, solved_routes
    )
    return validation, validation_message, solved_routes, Tree


def validate_retrosynthesis_api_response(response, solved_routes) -> Tuple[str, str]:
    if response.status_code == 200 and solved_routes:
        return "success", ""
    if not solved_routes:
        return "failed", "No routes found for molecule"
    if response:
        if response.status_code != 200:
            return (
                "failed",
                "Error with retrosynthesis function. Please try again in a few minutes. "
                "If this is a repeated error please report this to admin@ai4green.app, with details of your error",
            )


def determine_retrosynthesis_error(retrosynthesis_base_url: str) -> str:
    url = f"{retrosynthesis_base_url}/"
    response_content = ""
    try:
        response = requests.get(url)
        response_content = json.loads(response.content["Message"])
    except Exception:
        return "Retrosynthesis server is down. If this problem persists you can report to admin@ai4green.app"
    if not response_content == "Retrosynthesis service is running":
        return (
            "retrosynthesis service is currently having technical issues. If this problem persists you can report "
            "to admin@ai4green.app"
        )
    return (
        "Error with retrosynthesis. You can report this problem to admin@ai4green.app"
    )
