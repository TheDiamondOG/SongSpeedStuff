from pydub import AudioSegment
import os
import shutil
import argparse
import subprocess
from rich.console import Console
import sys

console = Console()
tmp_dir = "temp_pls_ignore"

parser = argparse.ArgumentParser(description="Make audio cool without audacity")

parser.add_argument("-f", "--file", help="File you want to modify song", required=False)
parser.add_argument("-d", "--download", help="Download a video", required=False)
parser.add_argument("-n", "--nightcore", help="Make a song a nightcore song", action="store_true", required=False)
parser.add_argument("-s", "--slowed", help="Make a song a slowed song", action="store_true", required=False)
parser.add_argument("-ser", "--sloweder", help="Make a song a slowed but slower song", action="store_true", required=False)
parser.add_argument("-c", "--custom", help="Change the speed of the song your self (1.25 is the nightcore)", required=False)
parser.add_argument("-o", "--output", help="Name of the output file", required=False)

args = parser.parse_args()

def apply_effects(input_path, output_path, effect):
    sound = AudioSegment.from_file(input_path)
    if effect == "nightcore":
        octaves = 4 / 12  # x1.25
        new_rate = int(sound.frame_rate * (2.0 ** octaves))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate}).set_frame_rate(44100)
    elif effect == "slowed":
        octaves = -4 / 12  # Slow down by x0.8
        new_rate = int(sound.frame_rate * (2.0 ** octaves))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate}).set_frame_rate(44100)
    elif effect == "sloweder":
        octaves = -6 / 12  # Slow down by x0.5
        new_rate = int(sound.frame_rate * (2.0 ** octaves))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate}).set_frame_rate(44100)
    sound.export(output_path, format="mp3", bitrate="192k")

def custom_slowness(input_path, output_path, octaves):
    octaves = float(octaves)
    sound = AudioSegment.from_file(input_path)
    new_rate = int(sound.frame_rate * (octaves))
    console.print(octaves)
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate}).set_frame_rate(44100)
    sound.export(output_path, format="mp3", bitrate="192k")

def get_video_title(url):
    cmd = f"yt-dlp --get-title {url}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        title = result.stdout.strip()
        if not title:
            raise ValueError("No title found")
        return title
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}", file=sys.stderr)
        exit(1)
    except ValueError as e:
        print(f"Error retrieving title: {e}", file=sys.stderr)
        exit(1)

def download_audio(url):
    title = get_video_title(url)

    # Handle cases where title might be empty or contain invalid characters
    if not title:
        console.print("No title found for the video.", style="red")
        exit(1)
    title = title.replace('/', '_').replace('\\', '_')  # Sanitize filename

    cmd = (
        f"yt-dlp -f bestaudio/best --extract-audio --audio-format mp3 --audio-quality 192K "
        f"--output {tmp_dir}/cool_audio.mp3 {url}"
    )
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        console.print(f"Failed to download audio. Error: {result.stderr.decode()}", style="red")
        exit(1)

    return title

def process_audio():
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)

    path = ''
    base_filename = 'audio_file'

    if args.download:
        video_title = download_audio(args.download)
        path = tmp_dir + '/cool_audio.mp3'
        base_filename = video_title
    elif args.file:
        path = args.file
        base_filename = os.path.basename(path).split('.')[0]

    if not os.path.isfile(path):
        console.print(f"File not found: {path}", style="red")
        exit(1)

    output_file = None
    if args.nightcore:
        output_file = f"output/nightcore/{base_filename} Nightcore.mp3"
        if not os.path.exists("output/nightcore"):
            os.mkdir("output/nightcore")
        apply_effects(path, tmp_dir + "/temp_effect.mp3", "nightcore")
        console.print(f"Nightcore made: {output_file}", style="cyan")

    if args.slowed:
        output_file = f"output/slowed/{base_filename} Slowed.mp3"
        if not os.path.exists("output/slowed"):
            os.mkdir("output/slowed")
        apply_effects(path, tmp_dir + "/temp_effect.mp3", "slowed")
        console.print(f"Slowed audio made: {output_file}", style="cyan")

    if args.sloweder:
        output_file = f"output/sloweder/{base_filename} Sloweder.mp3"
        if not os.path.exists("output/sloweder"):
            os.mkdir("output/sloweder")
        apply_effects(path, tmp_dir + "/temp_effect.mp3", "sloweder")
        console.print(f"Sloweder audio made: {output_file}", style="cyan")

    if args.custom:
        output_file = f"output/custom/{base_filename} Custom.mp3"
        if not os.path.exists("output/custom"):
            os.mkdir("output/custom")
        custom_slowness(path, tmp_dir + "/temp_effect.mp3", args.custom)
        console.print(f"Custom audio made: {output_file}", style="cyan")

    if output_file:
        if not os.path.exists("output"):
            os.mkdir("output")

        if args.output:
            output_file = args.output

        shutil.move(tmp_dir + "/temp_effect.mp3", output_file)
        shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    process_audio()
