#This file looks for new folder inside user uploads and converts them to reel id they are not already converted#
import os
from text_to_audio import text_to_speech_file
import time
import subprocess


def text_to_audio(folder):
    print("TTA - ", folder)
    done_path = f"uploads/{folder}/done.txt"
    if os.path.exists(done_path):
        with open(done_path, "r") as f:
            text = f.read()
        print(text, folder)
        # Call to generate audio from text
        text_to_speech_file(text, folder)
    else:
        print(f"File not found: {done_path}")
   

def create_reel(folder):
        # TODO: Update the command with your ffmpeg or reel creation command
    command = ""  # e.g. 'ffmpeg ...' command as a single string
    try:
        if command.strip():
            subprocess.run(command, shell=True, check=True)
            print("CR -", folder)
        else:
            print(f"No command set for creating reel in folder {folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command for reel creation: {e}")
   

if __name__ =="__main__":
    while True:
        print("processing queue...")
        with open("done.txt","r") as f:

            done_folders = f.readlines()


        print("Current working directory:", os.getcwd())
    
        done_folders = [f.strip() for f in done_folders]
        folders = os.listdir("uploads")
        print(f"All folders: {folders}")
        print(f"Done folders: {done_folders}")

        for folder in folders:
            if (folder not in done_folders):
                text_to_audio(folder) # Generate the audio from desc.txt
                create_reel(folder)
                with open("done.txt","a") as f:
                    f.write(folder+"\n")

        time.sleep(4)  # Sleep for 10 seconds before checking a