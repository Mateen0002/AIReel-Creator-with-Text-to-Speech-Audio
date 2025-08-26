import os
import uuid
import time
import subprocess
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder path set

elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def text_to_speech_file(text: str, folder: str) -> str:
    response = elevenlabs.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    save_folder = os.path.join("uploads", folder)
    os.makedirs(save_folder, exist_ok=True)
    save_file_path = os.path.join(save_folder, "audio.mp3")
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"{save_file_path}: A new audio file was saved successfully!")
    return save_file_path

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        input_file = []

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(rec_id))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save uploaded files
        for key, value in request.files.items():
            file = request.files[key]
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
                input_file.append(filename)

        # Write filenames to desc.txt
        desc_path = os.path.join(folder_path, "desc.txt")
        with open(desc_path, "a") as f:
            for filename in input_file:
                f.write(filename + "\n")

        # Generate input.txt for ffmpeg concat (only jpg files)
        imgs = [f for f in os.listdir(folder_path) if f.lower().endswith(".jpg")]
        input_txt_path = os.path.join(folder_path, "input.txt")
        with open(input_txt_path, "w") as f:
            for img in imgs:
                f.write(f"file '{img}'\n")

        # Generate audio from description text if provided
        if desc:
            text_to_speech_file(desc, str(rec_id))

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

def process_folders():
    while True:
        with open("done.txt", "r") as f:
            done_folders = [item.strip() for item in f.readlines()]

        folders = os.listdir("uploads")
        for folder in folders:
            if folder not in done_folders:
                done_path = os.path.join("uploads", folder, "done.txt")
                # Generate audio if not exists
                desc_file = os.path.join("uploads", folder, "desc.txt")
                if os.path.exists(desc_file) and not os.path.exists(os.path.join("uploads", folder, "audio.mp3")):
                    with open(desc_file, "r") as df:
                        text = df.read()
                    print(f"Generating audio for folder {folder}")
                    text_to_speech_file(text, folder)
                # TODO: Add ffmpeg command string here to create reel using input.txt and audio.mp3
                # Example: command = f'ffmpeg -f concat -safe 0 -i uploads/{folder}/input.txt -i uploads/{folder}/audio.mp3 -vf "..." output_{folder}.mp4'
                command = "" # Update as needed
                if command:
                    try:
                        subprocess.run(command, shell=True, check=True)
                        print(f"Reel created for {folder}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error creating reel for {folder}: {e}")
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")
        time.sleep(4)

if __name__ == "__main__":
    app.run(debug=True)
