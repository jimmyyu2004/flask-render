from flask import Flask, request, send_file, jsonify, Response
from flask_cors import CORS
from get_places_test import get_places
from merge_csv_test import merge_files_func
import subprocess
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": "*"}})

@app.route('/api/generate_places', methods=['POST'])
def generate_places():
    data = request.json
    latitude, longitude = data.get('latitude'), data.get('longitude')
    radius = data.get('radius')

    places_csv = 'places_csv'

    get_places(latitude, longitude, radius, places_csv)

    return jsonify({"generatedPlacesPath": places_csv})

@app.route('/api/download_csv', methods=['GET'])
def download_csv():
    file_path = request.args.get('filePath')
    return send_file(file_path, as_attachment=True, download_name='places.csv')

@app.route('/api/scrape_contacts', methods = ['POST'])   
def scrape_contacts():
    data = request.json.get('data')
    app.logger.debug(f'Received data: {data}')
    generated_contacts_csv = "generated_contacts.csv"

    if data is None:
        app.logger.error('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    input_data = {
        'restaurantNames': data[0],
        'typeNames': data[1],
        'outputPath': generated_contacts_csv  # Specify the output path for the CSV file
    }

    input_json = json.dumps(input_data)
    app.logger.debug(f'Input JSON: {input_json}')

    try:
        result = subprocess.run(
            ['node', 'scrape_google_test.js'], 
            input=input_json,
            text=True,
            capture_output=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        app.logger.error(f'Error running Node.js script: {e.stderr}')
        return jsonify({'error': 'Error running Node.js script', 'details': str(e)}), 500

    return jsonify({'generatedContactsPath': generated_contacts_csv})

@app.route('/api/download_contacts_csv', methods=['GET'])
def download_contacts_csv():
    file_path = request.args.get('filePath')
    return send_file(file_path, as_attachment=True, download_name='generated_contacts.csv')

@app.route('/api/merge_files', methods=['POST'])
def merge_files():
    data = request.json.get('data')
    merged_file_csv = 'merged_file.csv'

    places_file = data[0]
    contacts_file = data[1]

    merge_files_func(places_file, contacts_file, merged_file_csv)

    return jsonify('mergedFilePath:', merged_file_csv)

@app.route('/api/download_merge_files', methods=['GET'])
def download_merged_csv():
    file_path = request.args.get('filePath')
    return send_file(file_path, as_attachment=True, download_name='merged_file.csv')

if __name__ == "__main__":
    app.run(port=5000, debug=True)



