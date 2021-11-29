import os
import subprocess
import urllib3
import requests


def show_macroblocks_motvect(path, output_name):
    # http://trac.ffmpeg.org/wiki/Debug/MacroblocksAndMotionVectors
    # ffmpeg -flags2 +export_mvs -i cut_BBB.mp4 -vf codecview=mv=pf+bf+bb cut_BBB_motvect.mp4

    subprocess.call(["ffmpeg", "-flags2", "+export_mvs", "-i", path, "-vf",
                     "codecview=mv=pf+bf+bb",
                     output_name])


def repackage_aac_mp3(path, start, seconds, output_name):
    # ffmpeg -i BBB.mp4 -ss 20 -t 10 -c:v copy -an cut_noaudio_BBB.mp4
    subprocess.call(["ffmpeg", "-accurate_seek", "-i", path,"-ss", str(start),
                     "-t", str(seconds), "-an", "temp_video.mp4"])
    #"-accurate_seek", "-c:v", "copy"
    # mp3   ffmpeg -i trimmed_vid.mp4 -ss 20 -t 5 -c:a libmp3lame test_copy.mp3
    subprocess.call(["ffmpeg", "-i", path,"-ss", str(start), "-t", str(seconds),
                    "-c:a", "libmp3lame", "temp_audio_mp3.mp3"])

    # aac
    subprocess.call(["ffmpeg", "-i", path,"-ss", str(start), "-t", str(seconds),
                     "-c:a", "aac","-b:a", "64k", "temp_audio_aac.aac"])

    # repackage. ffmpeg -i temp_video.mp4 -i temp_audio_mp3.mp3 -i temp_audio_aac.aac -c:v copy -c:a copy -map 0:0 -map 1:a -map 2:a repackaged_vid.mp4
    subprocess.call(["ffmpeg", "-i", "temp_video.mp4", "-i",
                     "temp_audio_mp3.mp3", "-i", "temp_audio_aac.aac", "-c:v", "copy", "-c:a",
                     "copy", "-map", "0:0", "-map", "1:a", "-map", "2:a", output_name])

    # issues:https://ffmpeg.org/ffmpeg.html#:~:text=%2Dss%20position%20(input/output)
    # https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax

    if os.path.exists("temp_video.mp4"):
        os.remove("temp_video.mp4")
    if os.path.exists("temp_audio_mp3.mp3"):
        os.remove("temp_audio_mp3.mp3")
    if os.path.exists("temp_audio_aac.aac"):
        os.remove("temp_audio_aac.aac")


def detect_standards(path):
    # part 3 ffprobe
    # DVB EU mpeg2 h264/aac mp3, ATSC NA mpeg2 h264/ac3, DTMB CH AVS/DRA, ISDB JP BR mpeg2 h264/aac.
    # https://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call

    # test = subprocess.check_output(["ffprobe", "-i", "repackaged_vid.mp4"])
    # test = subprocess.Popen(["ffprobe", "-i", "repackaged_vid.mp4","2>&1"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    bash_output = subprocess.run(["ffprobe", "-i", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # import pdb;pdb.set_trace()
    # print(test2.communicate())

    # print("THIS IS THE GRABBED OUTPUT:", test.decode('ascii'))

    print("THIS IS THE GRABBED OUTPUT:", bash_output.stdout)
    splitted_out = bash_output.stdout.split()
    print(splitted_out)
    info_video = []
    info_audio = []
    for i, j in enumerate(splitted_out):
        if j == 'Video:':
            info_video.append((splitted_out[i+1]))
        elif j == 'Audio:':
            info_audio.append((splitted_out[i+1]))

    print(info_video)
    print(info_audio)
    print ('h264' in info_video)
    # Set the possible broadcast standards. Assume only 1 video
    if (('h264' in info_video or 'mpeg2video' in info_video) and ( 'aac' in info_audio)):
        print("2 Possible Broadcast Standards: DVB (EU) and ISDB (JP & BR)")
    elif (('h264' in info_video or 'mpeg2video' in info_video) and ("mp3" in info_audio)):
        print("Compatible Broadcast Standard: DVB (EU)")
    elif (('h264' in info_video or 'mpeg2video' in info_video) and ( "ac3" in info_audio)):
        print("Compatible Broadcast Standard: ATSC (NA)")
    elif (("AVS" in info_video or "AVS2" in info_video) and ("DRA" in info_audio)):
        print("Compatible Broadcast Standard: DTMB (CA)")
    else:
        print("ERROR: No compatible Broadcast Standard with codecs: video: ",
              info_video, " and audio:", info_audio)


def open_caption_subt(path, link, output_name):  #path, link_of_subt FALTA PATH I LINK
    # https://www.tutorialspoint.com/downloading-files-from-web-using-python
    # https://dl.opensubtitles.org/es/download/file/1957452335
    # Link https://dl.opensubtitles.org/en/download/file/1957451140
    if link == str(0):   # Random Hawkeye srt
        default_link = "https://dl.opensubtitles.org/es/download/file/1957452335"
        r = requests.get(default_link)
        with open("temp_subt.srt", "w") as file:
            file.write(r.text)
    else:
        r = requests.get(link)
        if r.ok:
            with open("temp_subt.srt","w") as file:
                file.write(r.text)
        else:
            print("Failed download! Exiting")
            return

    # ffmpeg -i mymovie.mp4 -vf subtitles=subtitles.srt mysubtitledmovie.mp4
    subprocess.call( ["ffmpeg", "-i", path, "-vf", "subtitles=temp_subt.srt",
             output_name])

    # Remove the temporary files
    if os.path.exists("temp_subt.srt"):
        os.remove("temp_subt.srt")


if __name__ == '__main__':

    program = int(input("Choose what program to run: \n1. Show Macroblocks and"
                        " motion vectors"
                        "\n2. Repackage with 2 audio streams (aac & mp3) "
                        "\n3. Check broadcast"
                        "\n4. Open Caption to video\n"))

    if program == 1:
        path = input("Enter path to video file you see the macroblocks and the"
                     " motion vectors: ")
        output_name = input("Name of output file: ")
        show_macroblocks_motvect(path, output_name)
    elif program == 2:
        path = input("Enter path to video file you want to repackage with mp3 "
                     "and aac: ")
        start = input("\nStarting position of the video:\n(Format: MM:SS, "
                      "see: https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax)\n")
        seconds = int(input("Length in seconds of video: "))
        output_name = input("Name of output file: ")
        repackage_aac_mp3(path, start, seconds, output_name)
    elif program == 3:
        path = input("Enter path to video file you want to detect standard: ")
        detect_standards(path)
    elif program == 4:
        path = input("Enter path to video file you want to 'burn' open "
                     "captions to: ")
        link = input("URL to an srt. If you don't have one, it will use a "
                     "default one: \n0. Use default \n")
        output_name = input("Name of output file: ")
        open_caption_subt(path, link, output_name)
    else:
        print("Program not valid")
