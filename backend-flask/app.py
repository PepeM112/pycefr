from flask import Flask, Blueprint, jsonify, request
from db_utils import *

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/levels', methods=['GET'])
def levels():
    return jsonify(get_levels())

@api.route('/origins', methods=['GET'])
def origins():
    return jsonify(get_origins())

@api.route('/classes', methods=['GET'])
def classes():
    return jsonify(get_classes())

@api.route('/analyses', methods=['GET'])
def analyses():
    return jsonify(get_analyses())

@api.route('/analyses/<int:analysis_id>/classes', methods=['GET'])
def analysis_classes(analysis_id):
    return jsonify(get_analysis_classes(analysis_id))

@api.route('/analyses', methods=['POST'])
def add_analysis():
    data = request.get_json()
    
    required_fields = ['name', 'origin_id', 'classes']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    analysis_id = create_analysis(
        name=data['name'],
        origin_id=data['origin_id'],
        classes=data['classes']
    )
    
    if analysis_id:
        return jsonify({'id': analysis_id}), 201
    else:
        return jsonify({'error': 'Failed to create analysis'}), 500

app = Flask(__name__)
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)