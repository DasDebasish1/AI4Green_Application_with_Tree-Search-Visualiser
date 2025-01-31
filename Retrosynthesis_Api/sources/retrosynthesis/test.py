import os
from aizynthfinder.interfaces import aizynthcli
from classes import RetroRoute
from startup import finder
import json
import time



def retrosynthesis_process(smiles):
	"""
	Takes a smiles string and returns a list of retrosynthetic routes stored as dictionaries
	"""
	# load config containing policy file locations
	aizynthcli._process_single_smiles(smiles, finder, None, False, None, [])
	# Find solved routes and process routes objects into list of dictionaries
	routes = finder.routes
	solved_routes = []
	for idx, node in enumerate(routes.nodes):
		if node.is_solved is True:
			solved_routes.append(routes[idx])
	solved_routes = solved_routes[0:10]
	solved_route_dict = {}
	for idx, route in enumerate(solved_routes, 1):
		retro_route = RetroRoute(route['dict'])
		retro_route.find_child_nodes2(retro_route.route_dict)
		route_dic = {'score': route['all_score']['state score'], 'steps': retro_route.reactions,
		             'depth': route['node'].state.max_transforms}
		solved_route_dict.update({f'Route {idx}': route_dic})
	route_dicts = routes.dicts[0:10]
	raw_routes = []
	for idx, route_dict in enumerate(route_dicts, 1):
		raw_routes.append(route_dict)

	return solved_route_dict, raw_routes
retrosynthesis_process("CCOC(=O)c1c(C2CC2)csc1NC(=O)COC(=O)c1cc(C)n(-c2cc(Cl)ccc2OC)c1C")