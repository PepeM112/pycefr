from flask import Flask, jsonify, request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import db_utils
from models.analysis import *
from models.catalog import *

app = FastAPI(title="PyCefr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/classes", response_model=List[ClassItem])
def get_classes():
    return db_utils.get_classes()


@app.get('/api/analyses', response_model=List[Analysis])
def get_analyses():
    return db_utils.get_analyses()


@app.get('/api/analyses/{analysis_id}', response_model=Analysis)
def get_analysis(analysis_id: int):
    analysis = db_utils.get_analysis(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get('/api/analyses/{analysis_id}/classes', response_model=List[AnalysisClass])
def get_analysis_classes(analysis_id: int):
    return db_utils.get_analysis_classes(analysis_id)


@app.post('/api/analyses', status_code=201)
def create_analysis(params: AnalysisCreate):
    data = request.get_json()

    required_fields = ['name', 'origin_id', 'classes']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    analysis_id = db_utils.create_analysis(
        name=data['name'],
        origin_id=data['origin_id'],
        classes=data['classes']
    )

    if analysis_id:
        return jsonify({'id': analysis_id}), 201
    else:
        return jsonify({'error': 'Failed to create analysis'}), 500


if __name__ == '__main__':
    app.run(debug=True)
