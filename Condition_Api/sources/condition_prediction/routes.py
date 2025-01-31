from sources.condition_prediction.startup import conditions_model
import json
import os
import time
from flask import Flask, request
from sources import app

ACCESS_KEY = os.getenv("KEY", "retro_key")



@app.route('/', methods=['GET'])
def service_check():
	page_data = {'Message': 'Service is running', 'Timestamp': time.time()}
	json_dump = json.dumps(page_data)
	return json_dump


@app.route('/condition_prediction_api/', methods=['GET'])
def condition_prediction():
	"""
	for NeuralNetContextRecommender.get_n_conditions
	Input: smiles string in format 'reactants.reactants2>>products'
	Output: tuple containing 2 lists
		list 1 index:
			0: temperature
			1: solvent
			2: reagent/base
			3: catalyst
			4: ? float
			5: ? float
			6: ? None
			7: False
		list 2:
			scores

	:return:
	"""

	access_key = str(request.args.get('key'))
	if access_key != ACCESS_KEY:
		return json.dumps({'Message': 'invalid key', 'Timestamp': time.time()})
	smiles = str(request.args.get('smiles'))
	# solved_route_dict_ls = retrosynthesis_process(smiles)
	predicted_conditions_results = conditions_model.get_n_conditions(smiles, 10, with_smiles=False, return_scores=True)
	predicted_conditions_cleaned = []
	for idx, predicted_conditions in enumerate(predicted_conditions_results[0]):
		prediction_conditions_dict = {'temperature': predicted_conditions[0],
		                              'solvent': predicted_conditions[1],
		                              'reagents': predicted_conditions[2],
		                              'catalyst': predicted_conditions[3],
		                              'score': predicted_conditions_results[1][idx]
		                              }
		predicted_conditions_cleaned.append(prediction_conditions_dict)
	page_data = {'Message': predicted_conditions_cleaned, 'Timestamp': time.time()}
	json_dump = json.dumps(page_data)
	return json_dump
