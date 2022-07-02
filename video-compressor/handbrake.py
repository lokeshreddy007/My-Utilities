import subprocess
import os
import sys
from shutil import copyfile
from pathlib import Path

# Path to the video you would like to compress
root_video_directory = sys.argv[1]

# Handbrake preset file
# [if you want you can use my custom handbrake preset which is available at this https://github.com/lokeshreddy007/My-Utilities/]
preset_file_path = sys.argv[2] 

# Format of the input video file ex:mp4
format = sys.argv[3] 

print(root_video_directory,preset_file_path,format)

# Check if HandBrakeCLI installed on this system or not
def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    # from whichcraft import which
    from shutil import which

    return which(name) is not None

# if the HandBrakeCLI is not installed in the system, it will install
if  not is_tool('HandBrakeCLI') :
    try:
        print("Installing Hand Brake CLI..... Please Wait...")
        os.system('sudo add-apt-repository ppa:stebbins/handbrake-releases -y')
        os.system('sudo apt install -y handbrake-cli')
    except:
        exit("Failed to install the handbrake-cli")

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
