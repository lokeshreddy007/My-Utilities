import subprocess
import os
import sys
from shutil import copyfile
from pathlib import Path

# mapping video source using volume to docker container input folder
root_video_directory = "/input"

# Handbrake preset file
# [if you want you can use my custom handbrake preset which is available at this https://github.com/lokeshreddy007/My-Utilities/]
preset_file_path = "preset.json"

# Format of the input video file ex:mp4
format = os.environ['FORMAT'] 

print(root_video_directory,preset_file_path,format)

# check for videos and compress
for path, directories, files in os.walk(root_video_directory):
    for file in files:
        if file.endswith("."+format):
            split_file = file.split('/')
            file_name = split_file[len(split_file) -1].replace('mp4','mkv')
            # input file path
            avi_file = os.path.join(path, file)
            #output file path
            output_file = os.path.join(path, file_name)
            # handbrake command
            handbrake_command = ['HandBrakeCLI', "-v" , "--preset-import-file", preset_file_path, '-i', f'{avi_file}',"-o", output_file]
            process = subprocess.Popen(handbrake_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            for line in process.stdout:
                print(line)
            os.remove(avi_file)
