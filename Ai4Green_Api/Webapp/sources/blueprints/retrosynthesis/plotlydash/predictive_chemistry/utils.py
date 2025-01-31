import base64
from typing import List

from pikachu.general import read_smiles, svg_string_from_structure
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from sources import models
from sources.extensions import db

from ..style_sheets import CytoscapeStyles as cytoStyles
from .compounds import ion_check

scale_factor = cytoStyles.scale_factor


def sig_figs_on_numbers(condition_set):
    keys_to_replace = {"score": 2, "temperature": 0}
    for key, value in condition_set.items():
        if key in keys_to_replace.keys():
            condition_set[key] = round(value, keys_to_replace[key])


def get_smiles_to_name(smiles_ls: List[str], solvent=False):
    exceptions = {
        "O=C([O-])[O-].[K+]": "Potassium bicarbonate",
        "O=C([O-])[O-].[Na+]": "Sodium bicarbonate",
    }
    if type(smiles_ls) is str:
        smiles_ls = [smiles_ls]
    compound_name_list = []
    for smiles in smiles_ls:
        # turn to inchi
        inchi = smiles_to_inchi(smiles)
        # lookup in database
        if solvent:
            compound = solvent_from_inchi(inchi)
        else:
            compound = compound_from_inchi(inchi)
        if compound:
            compound_name_list.append(compound.name)
        elif smiles in exceptions.keys():
            compound_name_list.append(exceptions[smiles])
        else:
            compound_name_list.append(smiles)
    return ", ".join(compound_name_list)


def compound_from_smiles(smiles, solvent=False):
    inchi = smiles_to_inchi(smiles)
    # lookup in database
    if solvent:
        return solvent_from_inchi(inchi)
    else:
        return compound_from_inchi(inchi)


def compound_from_inchi(inchi: str) -> models.Compound:
    compound = (
        db.session.query(models.Compound).filter(models.Compound.inchi == inchi).first()
    )
    compound = "Not Found" if compound is None else compound
    return compound


def solvent_from_inchi(inchi: str) -> models.Solvent:
    solvent = (
        db.session.query(models.Compound.solvent)
        .filter(models.Compound.inchi == inchi)
        .first()
    )
    solvent = "Not Found" if solvent is None else solvent
    return solvent


def solvent_from_name(name: str) -> models.Solvent:
    solvent = (
        db.session.query(models.Solvent).filter(models.Solvent.name == name).first()
    )
    solvent = "Not Found" if solvent is None else solvent
    return solvent


def compound_from_id(compound_id: int) -> models.Compound:
    compound = (
        db.session.query(models.Compound)
        .filter(models.Compound.id == compound_id)
        .first()
    )
    compound = "Not Found" if compound is None else compound
    return compound


# def conditions_compound_manager(condition_set):
#     compound_keys = ["solvent", "reagent", "catalyst", "reactants", "product"]
#     add_name_keys_to_dict(condition_set, compound_keys)
#     for key, smiles in condition_set.items():
#         if key in compound_keys:
#             get_compound_data(condition_set, smiles, key)


def get_compound_data(condition_set, smiles, key):
    name_ls = []
    id_ls = []
    # print("pre ion", smiles)
    if ion_check(smiles):
        smiles_ls = ion_handler(smiles)
        # print(smiles, "post ion")
    else:
        smiles_ls = smiles.split(".")
    for smiles in smiles_ls:
        if key == "solvent":
            compound = compound_from_smiles(smiles, solvent=True)
        else:
            compound = compound_from_smiles(smiles)
        name_ls.append(compound.name)
        id_ls.append(compound.id)
    condition_set[f"{key}_name"] = name_ls
    condition_set[f"{key}_id"] = id_ls


def ion_handler(smiles):
    compound_test = compound_from_smiles(smiles)
    if compound_test:
        # then this is db
        return compound_test
    else:
        pass
        # try and  convert ions
    if get_smiles_to_name(smiles) != smiles:
        # print("ion in db")
        smiles = handle_ions(smiles)
    return smiles


def alt_smiles_to_image(smiles):
    mol = Chem.MolFromSmiles(smiles)
    d = rdMolDraw2D.MolDraw2DCairo(350, 300)
    d.drawOptions().minFontSize = 22
    d.drawOptions().maxFontSize = 22
    d.drawOptions().fixedBondLength = 500
    d.DrawMolecule(mol)
    d.FinishDrawing()
    img_data = d.GetDrawingText()

    # img_data = Chem.Draw.MolsToGridImage(mol, returnPNG=True, molsPerRow=1, subImgSize=(400, 400))
    img_data = base64.b64encode(img_data)
    img_data = img_data.decode()
    img_data = "{}{}".format("data:image/png;base64,", img_data)
    #
    #
    #
    # mol = Chem.MolFromSmiles(smiles)
    # img = Chem.Draw.MolToImage(mol)
    # img_data = img.text['rdkitPKL rdkit 2022.03.5']
    # img_data = img_data.encode('utf-8')
    # img_data = str(base64.b64encode(img_data), 'utf-8')
    # # binary_img_text =
    # # image_file = Chem.Draw.ReactionToImage(rxn, returnPNG=True, subImgSize=(100, 100))  # 16:9 image ratio - looks bad at moment 430 pixels
    # # img_data = base64.b64encode(bytes(img.text['rdkitPKL rdkit 2022.03.5']))
    # # img_data = img_data.decode()
    # img_data = "{}{}".format("data:image/png;base64,", img_data)
    return img_data


def smiles_to_image(smiles: str, get_dimensions=False) -> (str, int):
    """Takes a smiles string and returns an image data string
    Pikachu based
    """
    struc = read_smiles(smiles)
    try:
        mol_svg_string = svg_string_from_structure(struc)
    except AttributeError:  # TODO placeholder error
        return ""
    img_data = mol_svg_string.encode("utf-8")
    img_data = str(base64.b64encode(img_data), "utf-8")
    img_data = "{}{}".format("data:image/svg+xml;base64,", img_data)
    if get_dimensions is True:
        # find the viewbox size from the svg string
        viewbox_start_idx = mol_svg_string.find('viewBox="0 0 ') + 13
        viewbox_end_idx = mol_svg_string.find('" xmlns="http://www.w3.org/2000/svg')
        viewbox_data = mol_svg_string[viewbox_start_idx:viewbox_end_idx]
        width, height = [float(x) * scale_factor for x in viewbox_data.split(" ")]
        return img_data, width, height
    return img_data


def reaction_smiles_to_image(smiles: str) -> str:
    """Take a reaction smiles string and returns an image data string"""
    rxn = AllChem.ReactionFromSmarts(smiles, useSmiles=True)

    drawer = rdMolDraw2D.MolDraw2DCairo(450, 225)
    drawer.SetFontSize(6)
    drawer.maxFontSize = 6
    drawer.DrawReaction(rxn)
    drawer.FinishDrawing()
    image_file = drawer.GetDrawingText()

    # image_file = Chem.Draw.ReactionToImage(rxn, returnPNG=True, subImgSize=(100, 100))  # 16:9 image ratio - looks bad at moment 430 pixels
    img_data = base64.b64encode(image_file)
    img_data = img_data.decode()
    img_data = "{}{}".format("data:image/png;base64,", img_data)
    return img_data


def smiles_to_inchi(smiles: str) -> str:
    """
    Get the corresponding InChi from a SMILES string. Returns None if the smiles string is invalid

    Args:
       smiles: The compound's smiles string

    Returns:
        The compound's InChI string
    """
    mol = Chem.MolFromSmiles(smiles)
    return None if mol is None else Chem.MolToInchi(mol)


def handle_ions(smiles):
    compounds_ls = smiles.split(".")
    salts = []
    # for simple ions
    if smiles.count("+") == 1 and smiles.count("-") == 1:
        ions = [x for x in compounds_ls if any(charge in x for charge in ["+", "-"])]
        non_ions = [
            x for x in compounds_ls if not any(charge in x for charge in ["+", "-"])
        ]
        ionic_compound = ".".join(ions)
        compounds_ls = non_ions + [ionic_compound]
    else:
        # want to find if there is an adjacent item in the list
        for idx, compound in enumerate(compounds_ls):
            # code for more than 1 of each +/- in the smiles
            if "+" in compound:
                # check if the opposite symbol is in the next one
                try:
                    if "-" in compounds_ls[idx + 1]:
                        salts.append(
                            {
                                "smiles": ".".join(compounds_ls[idx : idx + 2]),
                                "indices": slice(idx, idx + 2),
                            }
                        )
                except IndexError:
                    pass
            elif "-" in compound:
                try:
                    if "+" in compounds_ls[idx + 1]:
                        salts.append(
                            {
                                "smiles": ".".join(compounds_ls[idx : idx + 2]),
                                "indices": slice(idx, idx + 2),
                            }
                        )
                except IndexError:
                    pass

            for salt in salts:
                del compounds_ls[salt["indices"]]
                compounds_ls.insert(salt["indices"].start, salt["smiles"])
    return compounds_ls


def functionality_disabled_check(functionality_status):
    if functionality_status == "disabled":
        return True
    return False


def get_current_route(routes, selected_route):
    selected_route_idx = int(selected_route[-1]) - 1  # minus 1 to use zero-based index
    current_route = routes[selected_route_idx]
    return current_route


def encodings_to_smiles_symbols(input_str: str) -> str:
    """Returns the string with the SMILES symbols restored, replacing the URL encodings."""
    return (
        input_str.replace("%23", "#")
        .replace("%2B", "+")
        .replace("%2D", "-")
        .replace("%40", "@")
    )


def get_workbook_from_id(workbook_id: int) -> models.WorkBook:
    """Returns a workbook object using the workbook id"""
    return (
        db.session.query(models.WorkBook)
        .filter(models.WorkBook.id == workbook_id)
        .first()
    )


def smiles_not_valid(smiles_regex: str):
    """
    Input is smiles regex pattern str.
    Returns Bool depending on if smiles is valid.
    """
    if "_invalid" in smiles_regex:
        return True
    return False
