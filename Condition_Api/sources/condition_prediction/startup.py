from sources.condition_prediction.askcos.synthetic.context.neuralnetwork import NeuralNetContextRecommender
import sources.condition_prediction.askcos.global_config as gc

conditions_model = NeuralNetContextRecommender()

conditions_model.load_nn_model(model_path=gc.NEURALNET_CONTEXT_REC['model_path'], info_path=gc.NEURALNET_CONTEXT_REC[
	'info_path'], weights_path=gc.NEURALNET_CONTEXT_REC['weights_path'])