from typing import Dict, List, Tuple

from dash import html
from flask_login import current_user
from sources.auxiliary import get_workbooks, get_workgroups


def make_workbooks_dropdown_options() -> Tuple[List[Dict], int]:
    """
    Makes the workbooks dropdown with all workbooks the active user belongs to
    Returns:
        A list of dictionaries with workbook names as 'label' and primary key integer id as 'value'
        An integer of the primary key id of the first workbook in the list to act as a default value.

    """
    workgroups = get_workgroups()
    workbooks = [get_workbooks(wg, "object") for wg in workgroups]
    # flatten nested lists
    workbooks = [workbook for sublist in workbooks for workbook in sublist]
    workbook_names = [wb.name for wb in workbooks]
    workbook_ids = [wb.id for wb in workbooks]
    workbook_options = [
        {"label": name, "value": int_id}
        for name, int_id in zip(workbook_names, workbook_ids)
    ]
    if workbook_ids:
        return workbook_options, workbook_ids[0]
    # if user is not in any workbooks
    return workbook_options, None


def make_conditions_dropdown(
    route: str,
    conditions_data: List[Dict],
    weighted_sustainability_data: Dict,
    tapped_node: Dict,
) -> Tuple[str, str, List[Dict]]:
    """
    Generate dropdown options based on reaction conditions and sustainability.

    Args:
        route (str): The route information.
        conditions_data: Data containing reaction conditions.
        weighted_sustainability_data: Data containing sustainability information.
        tapped_node: The selected node information.

    Returns:
        Reaction conditions,
        Reaction sustainability,
        dropdown options.
        Returns (None, None, None) if condition prediction is unsuccessful.
    """
    # change current route to zero index
    route_index = int(route[-1]) + -1
    conditions = conditions_data[route_index][route]
    sustainability = weighted_sustainability_data["routes"][route]["steps"]

    for (
        all_reaction_conditions,
        all_reaction_sustainability,
    ) in zip(conditions, sustainability):
        if list(all_reaction_conditions)[0] == tapped_node["id"]:
            reaction_conditions = all_reaction_conditions[tapped_node["id"]]
            if reaction_conditions == "Condition Prediction Unsuccessful":
                return None, None, None

            reaction_sustainability = all_reaction_sustainability[tapped_node["id"]]
            condition_set_labels = [
                f"Condition Set {x + 1}" for x in range(len(reaction_conditions))
            ]

            condition_set_styles = style_condition_set_dropdown(reaction_sustainability)

            condition_set_options = []
            for condition_set_label, style in zip(
                condition_set_labels, condition_set_styles
            ):
                condition_set_options.append(
                    {
                        "label": html.Span([f"{condition_set_label}"], style=style),
                        "value": condition_set_label,
                        "style": {"width": "150%"},
                        "width": "150%",
                    }
                )
            return reaction_conditions, reaction_sustainability, condition_set_options


def style_condition_set_dropdown(reaction_weighted_sustainability):
    hazard_colours = current_user.hazard_colors
    flag_score_to_phrase_dict = {
        4: "HighlyHazardous",
        3: "Hazardous",
        2: "Problematic",
        1: "Recommended",
    }
    # get weighted medians
    style_ls = []
    for condition_set in reaction_weighted_sustainability:
        weighted_median = round(condition_set["weighted_median"]["flag"], 0)
        chem21_phrase = flag_score_to_phrase_dict[weighted_median]
        background_colour = hazard_colours[chem21_phrase]
        text_colour = hazard_colours[f"{chem21_phrase}_text"]
        style_ls.append(
            {
                "background-color": background_colour,
                "color": text_colour,
                "width": "250%",
            }
        )
    return style_ls


def routes(active_retrosynthesis: Dict, active_weighted_sustainability: Dict):
    # get list of routes and then
    number_of_steps_ls = [
        len(route["steps"])
        for route in active_weighted_sustainability["routes"].values()
    ]
    route_ls = [f"Route {x + 1}" for x in range(len(active_retrosynthesis["routes"]))]
    route_style_ls = style_routes_dropdown(active_weighted_sustainability)
    route_options = []
    for route_label, style, steps in zip(route_ls, route_style_ls, number_of_steps_ls):
        route_options.append(
            {
                "label": html.Span([f"{route_label} ({steps})"], style=style),
                "value": route_label,
                "style": {"width": "150%"},
                "width": "150%",
            }
        )
    return route_options


def style_routes_dropdown(weighted_sustainability: Dict) -> List[Dict]:
    """
    Style routes dropdown based on weighted sustainability scores.

    Args:
        weighted_sustainability Weighted sustainability data.

    Returns:
        A list of styles for routes dropdown based on weighted sustainability scores. 1 style per route.
    """
    hazard_colours = current_user.hazard_colors
    flag_score_to_phrase_dict = {
        4: "HighlyHazardous",
        3: "Hazardous",
        2: "Problematic",
        1: "Recommended",
    }
    # get weighted medians
    style_ls = []
    for route in weighted_sustainability["routes"].values():
        weighted_median = route["route_average"]["weighted_median"]
        weighted_median = round(weighted_median, 0)
        chem21_phrase = flag_score_to_phrase_dict[weighted_median]
        background_colour = hazard_colours[chem21_phrase]
        text_colour = hazard_colours[f"{chem21_phrase}_text"]
        style_ls.append(
            {
                "background-color": background_colour,
                "color": text_colour,
                "width": "250%",
            }
        )
    # convert weighted median number to hazard color
    return style_ls
