import sys
from urllib import response
from moviepy.editor import VideoFileClip
import boto3
import urllib
import json
import time
import io
import os

transcribe_client = boto3.client('transcribe')
s3_client = boto3.client('s3',region_name='us-east-1')

def convert_video_to_audio(input_video_file,output_ext):
    filename,ext =os.path.splitext(input_video_file)
    clip = VideoFileClip(input_video_file)
    clip.audio.write_audiofile(f"{filename}.{output_ext}")


def upload_to_s3(file_name,bucket):
    object_name = os.path.basename(file_name)
    s3_client.upload_file(file_name,bucket,object_name)

def audio_to_text(audio_file,name):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=name,
        Media={'MediaFileUri':audio_file},
        MediaFormat='mp3',
        LanguageCode="ru-RU"
    )
    max_tries= 60
    while max_tries > 0:
        max_tries -= -1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=name)
        job_stat = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_stat in ['COMPLETED','FAILED']:
            if job_stat == 'COMPLETED':
                response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                data = json.loads(response.read())
                text = data['results']['transcripts'][0]['transcript']
                print("Extracted from audio file -------------")
                print(text)
            break
        else:
            print(job_stat)
        time.sleep(10)


if __name__ == '__main__':
    vf = "test.mp4"
    #convert_video_to_audio(vf,"mp3")
    #upload_to_s3("test.mp3","audio-converter-storage")
    audio_to_text("s3://audio-converter-storage/test.mp3","test_one")
    print(s3_client)
    