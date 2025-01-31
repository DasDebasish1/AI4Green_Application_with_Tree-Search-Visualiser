from flask import render_template, request, jsonify, flash, redirect, url_for, session,send_from_directory,send_file
from flask import current_app as app
from . import retrosynthesis_bp  # imports the blueprint of the reaction table route
from flask_login import login_required
from sources.auxiliary import get_workgroups, get_notification_number, get_workbooks, security_member_workgroup_workbook
from sources import models, services
from flask_login import current_user
import json
from .utils import draw_tree
from .plotlydash.predictive_chemistry.conditions_api import get_conditions
from .plotlydash.predictive_chemistry import sustainability
import os
from io import BytesIO
from .plotlydash.predictive_chemistry import conditions_api
from .plotlydash.predictive_chemistry import sustainability
from .plotlydash.predictive_chemistry.utils import (
    smiles_to_inchi,
)

@retrosynthesis_bp.route('/retrosynthesis/', methods=['GET', 'POST'])
@login_required
def retrosynthesis():
	workgroups = get_workgroups()
	notification_number = get_notification_number()
	current_user.retrosynthesis_smiles = request.form['smiles']
	print("retrosynthesis routes", current_user.retrosynthesis_smiles)
	return '', 204

#add
@retrosynthesis_bp.route('/retrosynthesis_tree', methods=['GET'])
@login_required
def reaction_tree():
	with open(f'CacheTrees/{current_user.username}.json', "r") as json_file:
		data = json_file.read()

	return render_template('reaction_tree.html',data=data)

@retrosynthesis_bp.route('/retrosynthesis_save_tree', methods=['GET'])
@login_required
def save_reaction_tree():
	#data = request.get_json()
	with open(f'CacheTrees/{current_user.username}.json', "r") as json_file:
		data = json_file.read()
	im = draw_tree(json.loads(data),f'CacheTrees/{current_user.username}.png')
	im.save(os.path.join(app.root_path, f'static/CacheTrees/{current_user.username}.png'))
	#return app.root_path
	return send_from_directory(app.static_folder+"/CacheTrees", f"{current_user.username}.png",as_attachment=True)
###
@retrosynthesis_bp.route('/get_condition_sustainibility', methods=['GET'])
@login_required
def get_condition_sustainibility():
	data={}
	reaction_smiles=request.args.get('reaction_smiles')
	#data = request.get_json()
	if reaction_smiles:
		conditions=conditions_api.get_reaction_condition(reaction_smiles)
		processed_conditions = conditions_api.ProcessConditions(conditions, "","").process_conditions()
		conditions=[]
		for condition in processed_conditions:
			sustainabilit = sustainability.ReactionSustainabilityFlags(condition)
		
			sustainabilit.get_sustainability_flags()
		# # mean_score = np.mean(sustainability_flags)
		# # sustainability.average_sustainability_score = mean_score
			sustainability_dict = sustainabilit.to_dict()
			conditions.append(sustainability_dict)
		data["conditions"]=conditions
		data["sus"]=processed_conditions

	else:
		data["conditions"]=[]
		data["sus"]=[]
	
	
	
	return data


@retrosynthesis_bp.route('/get_compound', methods=['GET'])
def get_compound():
	smiles=request.args.get('smiles')
	inchi = smiles_to_inchi(smiles)
	if inchi is None:
		return {"Compound":[]}
	compound_object = services.compound.get_compound_from_inchi(inchi)
	if compound_object is None:
		#return f"Compound with SMILES {smiles} is not in the database"
		return {"Compound":[]}

	
	return {"Compound": [
                compound_object.name,
                compound_object.molec_weight,
                compound_object.cas,
                compound_object.hphrase,
            ]}

