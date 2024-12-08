from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Initialize default language
config = {
    "azure_voice": "ro-RO"  # Default language
}

config2 = {
    "hour": "07:00"  # Default wake-up hour
}


@app.route('/api/set-language', methods=['POST'])
def set_language():
    try:
        # Parse the JSON payload from the request
        data = request.get_json()
        language = data.get('language')

        if not language:
            return jsonify({"error": "Language variable is missing."}), 400

        # Update the language in the configuration
        config['azure_voice'] = language

        return jsonify({"message": "Language updated successfully.", "azure_voice": config['azure_voice']}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/get-language', methods=['GET'])
def get_language():
    return jsonify({"azure_voice": config['azure_voice']}), 200


@app.route('/api/set-hour', methods=['POST'])
def set_hour():
    print("äsdsdasd")
    try:
        # Parse the JSON payload from the request
        data = request.get_json()
        hour = data.get('hour')

        if not hour:
            return jsonify({"error": "Hour variable is missing."}), 400

        # Update the language in the configuration
        config2['hour'] = hour

        return jsonify({"message": "Hour updated successfully.", "hour": config2['hour']}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/get-hour', methods=['GET'])
def get_hour():
    return jsonify({"hour": config2['hour']}), 200


if __name__ == '__main__':
    app.run()