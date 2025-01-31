from flask import Blueprint

condition_prediction_bp = Blueprint('condition_prediction', __name__)

from sources.condition_prediction import routes
