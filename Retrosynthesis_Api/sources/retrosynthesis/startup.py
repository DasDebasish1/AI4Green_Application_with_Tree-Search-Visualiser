import os
from sources.retrosynthesis.classes import AiZynthArgs
from aizynthfinder import aizynthfinder
from aizynthfinder.interfaces import aizynthcli

BASEDIR = os.path.dirname(__file__)



AIZYNTH = {
	'policy': {
		'files': {
			'full_uspto': [os.path.join(BASEDIR, 'AiZynthfinder', 'full_uspto_03_05_19_rollout_policy.hdf5'),
			               os.path.join(BASEDIR, 'AiZynthfinder', 'full_uspto_templates.hdf5')]}},
	'stock': {
		'files': {
			'zinc': os.path.join(BASEDIR, 'AiZynthfinder', 'zinc_stock_17_04_20.hdf5'),
			# 'stock': os.path.join(BASEDIR, 'AiZynthfinder', 'aizynth_n1_stock.txt')
		}
	},
	'config_file': os.path.join(BASEDIR, 'AiZynthfinder', 'aizynthfinder_config.yml'),
	# 'properties': {
	# 	'max_transforms': 10,
	# 	'time_limit': 3600,
	# 	'iteration_limit': 500,
	#
	#
	# }

}

print("1")
print(AIZYNTH)
aizynth_config_dic = AIZYNTH
print(2)
# initiate object containing all required arguments
args = AiZynthArgs("placeholder", aizynth_config_dic['config_file'], aizynth_config_dic['policy'],
				   aizynth_config_dic['stock'])
print(3)
# AiZynthFinder object contains results data
finder = aizynthfinder.AiZynthFinder(configdict=aizynth_config_dic)
print(4)
# set up stocks, policies, then start single smiles process
aizynthcli._select_stocks(finder, args)
print(5)
finder.expansion_policy.select(args.policy or finder.expansion_policy.items[0])
print(6)
finder.filter_policy.select(args.filter)
print(7)