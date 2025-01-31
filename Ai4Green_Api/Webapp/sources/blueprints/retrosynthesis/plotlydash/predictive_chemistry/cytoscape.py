from typing import Dict

import pandas as pd

from ..style_sheets import CytoscapeStyles as cytoStyle
from .utils import smiles_to_image

node_border_dict = cytoStyle.node_border_dict


class RetrosynthesisCytoscape:
    def __init__(self, solved_routes: Dict, selected_route: str):
        self.solved_routes = solved_routes
        self.selected_route_idx = int(selected_route[-1]) - 1
        # update from 1-based index in frontend to a 0 based index
        # zero_based_index = int(selected_route[-1]) - 1
        self.displayed_route = solved_routes[selected_route]
        self.node_df = self.make_node_dataframe()

    def make_cytoscape_elements(self):
        nodes = self.make_nodes()
        edges = self.make_edges()
        elements = nodes + edges
        return elements

    def make_cytoscape_stylesheet(self):
        chemical_image_stylesheet = self.make_chemical_image_stylesheet()
        new_stylesheet = cytoStyle.basic_stylesheet + chemical_image_stylesheet
        return new_stylesheet

    def make_node_dataframe(self):
        # make dataframe where each row is a node, index is node_id, columns are smiles and node type
        node_ls = []
        for node in self.displayed_route["steps"]:
            node_type = self.get_node_type(node)
            node_reaction_smiles = self.get_node_reaction_smiles(node)
            node_ls.append(
                {
                    "smiles": node["smiles"],
                    "node_type": node_type,
                    "reaction_class": node["reaction_class"],
                    "reaction_smiles": node_reaction_smiles,
                }
            )
        node_ids = [x["node_id"] for x in self.displayed_route["steps"]]
        node_df = pd.DataFrame(node_ls, index=node_ids)
        return node_df

    @staticmethod
    def get_node_reaction_smiles(node):
        reaction_smiles = ""
        if node["child_smiles"]:
            reactants = ".".join(node["child_smiles"])
            reaction_smiles = reactants + ">>" + node["smiles"]
        return reaction_smiles

    @staticmethod
    def get_node_type(node):
        if not node["child_smiles"]:
            node_type = "terminal"
        elif node["node_id"] == "node-0":
            node_type = "target"
        else:
            node_type = "normal"
        return node_type

    def make_nodes(self):
        """This makes the nodes with the corresponding id and smiles string as the label"""
        # make the coordinate lists

        x_ls, y_ls = [], []
        for node_id in self.node_df.index:
            depth = int(node_id.split("-")[1])
            row_position = int(node_id.split("-")[-1]) + 1
            number_of_elements_in_row = len(
                [x for x in self.node_df.index if int(x.split("-")[1]) == depth]
            )
            x = (
                500 / number_of_elements_in_row / 2 * row_position
            )  # if 1 elem 400/1 = 400 400/2=200
            y = depth * 50
            # print(f'{node_id=}, {x=}, {y=}')
            x_ls.append(x)
            y_ls.append(y)

        nodes = [
            {
                "data": {
                    "element": "node",
                    "id": node_id,
                    "smiles": smiles,
                    "reaction_smiles": reaction_smiles,
                    "label": reaction_class,
                    "type": node_type,
                },
                # 'position': {'x': x, 'y': y},
            }
            for node_id, smiles, reaction_smiles, reaction_class, node_type in zip(
                self.node_df.index,
                self.node_df["smiles"],
                self.node_df["reaction_smiles"],
                self.node_df["reaction_class"],
                self.node_df["node_type"],
            )
        ]
        return nodes

    def make_edges(self):
        """This returns a list of edges to connect the nodes"""
        sources, targets, labels = [], [], []
        for step in self.displayed_route["steps"]:
            source = step["node_id"]
            # find children node id by their smiles
            for child in step["child_smiles"]:
                # find node with the smiles
                for idx, smiles in enumerate(self.node_df["smiles"]):
                    if child == smiles:
                        target_idx = idx
                target_id = self.displayed_route["steps"][target_idx]["node_id"]
                sources.append(source), targets.append(target_id), labels.append(
                    f'{step["smiles"]} to {child}'
                )
        edges = [
            {
                "data": {
                    "element": "edge",
                    "id": f"{source}_{target}",
                    "source": source,
                    "target": target,
                }
            }
            for source, target in zip(sources, targets)
        ]
        return edges

    def make_chemical_image_stylesheet(self):
        """This returns the stylesheet which matches the node id to the png string to show the image"""

        img_ls = []
        width_ls = []
        height_ls = []
        for smiles in self.node_df["smiles"]:
            img_data, width, height = smiles_to_image(smiles, get_dimensions=True)
            img_ls.append(img_data)
            width_ls.append(width)
            height_ls.append(height)
        chemical_image_stylesheet = [
            {
                "selector": "#" + node_id,
                "style": {
                    "background-image": rxn_image,
                    "width": width * 0.75,
                    "height": height * 0.75,
                    "background-width": width,
                    "background-height": height,
                    "border-color": node_border_dict[node_type]["colour"],
                    "border-style": node_border_dict[node_type]["style"],
                    "border-width": node_border_dict[node_type]["width"],
                },
            }
            for node_id, rxn_image, width, height, node_type in zip(
                self.node_df.index,
                img_ls,
                width_ls,
                height_ls,
                self.node_df["node_type"],
            )
        ]
        return chemical_image_stylesheet
