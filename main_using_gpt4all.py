# Import necessary libraries and modules
from flask import Flask, render_template, request, jsonify
import openai
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment
from flask_socketio import SocketIO, emit
from function_manager import FunctionManager
import json

# Create a Flask application and configure its static folder
app = Flask(__name__, static_folder='static')

# Initialize a SocketIO instance for real-time communication
socketio = SocketIO(app)

# Create an instance of the FunctionManager class
fm = FunctionManager()

# Read the OpenAI API key from an external file
api_key = ''
with open('api.key', 'r') as file:
    api_key = file.read().strip()
    
openai.api_base = "http://192.168.8.103:4891/v1"

# Set the OpenAI API key
openai.api_key = api_key

# Create a dictionary to store monitor data, which is used for real-time messaging
monitor_map = {}

# Handle the connection of a user to the SocketIO namespace
@socketio.on('connect', namespace='/sio')
def handle_connect():
    print('A user connected')

# Handle the connection of a monitor to the SocketIO namespace and store monitor data
@socketio.on('monitor_connect', namespace='/sio')
def handle_monitor_connect(data):
    print(data)

    # Store monitor data in the map
    monitor_map[request.sid] = {
        'status': 'online',
        'target_id': data['target_id'],
        'my_id': request.sid
    }

# Handle incoming messages and forward them to the appropriate monitors
@socketio.on('message', namespace='/sio')
def handle_message(data):
    print(data)
    target_id = request.sid

    # Find monitors that match the target_id and forward the message
    for sid, monitor_data in monitor_map.items():
        if monitor_data['target_id'] == target_id:
            print(f'Sending data to: {monitor_data["my_id"]}')
            emit('message', data, room=monitor_data['my_id'])

# Define an endpoint to get system roles and return them as JSON
@app.route('/get_system_roles', methods=['GET'])
def get_system_roles():
     return jsonify(fm.get_system_roles())

# Define an endpoint for sending messages to GPT-3 and processing responses
@app.route('/chatgpt/send', methods=['POST'])
def send_gpt():
    conversation = (request.json)
    functions = fm.get_functions()

    prompt = conversation[-1]['content']

    # Create a chat conversation with GPT-3
    response = openai.Completion.create(
		model='gpt4all-13b-snoozy-q4_0',
		prompt=prompt,
		functions=functions,
		function_call="auto",
		max_tokens=2000,
		tempurature=0.2,
		top_p=0.1,
		n=1,
		echo=True,
		stream=False
    )

    print(response)
    
    # Extract and return the generated reply, or execute a command if present
    reply = response.choices[0].text
    command = fm.extract_command(json.dumps(reply))
    if command:
        function_response = fm.execute_command(command)
        function_confirmation = append_function_response(conversation, function_response, functions)
        convo_return = function_confirmation
    else:
        convo_return = append_message(conversation, reply)

    return(convo_return)

# Define an endpoint for text-to-speech (TTS) conversion
@app.route('/g/tts', methods=['POST'])
def tts(language='en', output_file='./static/raw_audio/output.mp3'):

	# Create a gTTS object and specify the language
	tts = gTTS(text=request.json['text'], lang=language, slow=False)

	# Save the speech as an MP3 file
	tts.save(output_file)

	return(output_file)

# Define an endpoint for speech-to-text (STT) conversion
@app.route('/g/stt', methods=['POST'])
def speech_to_text():
    if 'outputFile' not in request.json:
        return jsonify({'error': 'No audio file provided'})

    audio_file = request.json['outputFile']

    # Perform speech recognition
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)  # Use Google Web API for recognition

        return jsonify({'transcript': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Speech recognition could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition request failed: {str(e)}'})

# Define an endpoint for serving static files
@app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    # Define the directory where your files are located
    file_directory = './static/raw_audio/'  # Replace with the Path to your files

    # Generate the full path to the requested file
    file_path = os.path.join(file_directory, filename)

    # Check if the file exists
    if os.path.exists(file_path):
        return(file_path)
    else:
        return "File not found", 404

# Define an endpoint for serving image files
@app.route('/uploads/<filename>', methods=['GET'])
def serve_image(filename):
    # Define the directory where your files are located
    file_directory = './uploads/'  # Replace with the Path to your files

    # Generate the full path to the requested file
    file_path = os.path.join(file_directory, filename)

    # Check if the file exists
    if os.path.exists(file_path):
        return(file_path)
    else:
        return "File not found", 404

# Define an endpoint for trimming and processing audio files
@app.route('/trimAudio', methods=['POST'])
def trim_audio():
    audio_file = request.files.get('webm')

    if not audio_file:
        return jsonify({'error': 'No audio file provided'})

    try:
        # Define file paths
        input_file_path = f'./uploads/{audio_file.filename}.webm'
        converted_file_path = './uploads/converted.wav'
        output_file_path = './uploads/trimmed.wav'

        # Save the uploaded audio file
        audio_file.save(input_file_path)

        # Convert the audio to WAV format using pydub
        audio = AudioSegment.from_file(input_file_path, format="ogg")
        audio.export(converted_file_path, format="wav")

        # Use FFmpeg to remove silence from the audio
        os.system(f'ffmpeg -i {converted_file_path} -af silenceremove=stop_periods=-1:stop_threshold=-35dB:stop_duration=0.72:window=0 {output_file_path} -y')

        # Clean up the temporary converted file
        os.remove(converted_file_path)

        return jsonify({'message': 'Processing finished!', 'outputFile': output_file_path})
    except Exception as e:
        return jsonify({'error': f'An error occurred during processing: {str(e)}'})

# Define an endpoint for saving image files
@app.route('/saveImage', methods=['POST'])
def save_image():
    image_file = request.files.get('jpeg')

    input_file_path = f'./uploads/file.jpeg'

    image_file.save(input_file_path)

    return jsonify({'message': 'Processing finished!', 'outputFile': input_file_path})

# Define the default endpoint for rendering an HTML template
@app.route('/')
def index():
    return render_template('gpt_chat.html')

# Define an endpoint for rendering a face.html template
@app.route('/face')
def face():
    return render_template('face.html')

# Helper function to append a message to a conversation
def append_message(conversation, message):
    conversation.append({'role': 'system', 'content': message})
    return conversation

# Helper function to append a function response to a conversation and execute it
def append_function_response(conversation, message, functions):
    append_message(conversation, message)
    prompt = conversation[-1]['content']
    # Create a chat conversation with GPT-3
    response = openai.Completion.create(
		model='gpt4all-13b-snoozy-q4_0',
		prompt=prompt,
        functions=functions,
        function_call="auto",
        max_tokens=2000,
        tempurature=0.2,
        top_p=0.1,
        n=1,
        echo=True,
        stream=False
    )
    return append_message(conversation, response.choices[0].message)

# Start the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
