"""
Text-to-Speech Synthesis Script using Amazon Polly
Converts text files to MP3 audio and uploads to S3
"""

import boto3
import os
import sys
from datetime import datetime

#initialize boto3 clients

polly_client = boto3.client('polly')
s3_client = boto3.client('s3')
converted_file = ""

def convert_text_to_speech(input_text_file_path, converted_file):
    """
    Converts text to speech using Amazon Polly
    """
    try:
        with open(input_text_file_path, 'w') as file: 
            text = file.read()
            converted_file = polly_client.synthesize_speech(
                Text=text,
                OutPutFormat='mp3',
                VoiceId='Joanna'
            )
        file.write(converted_file)
    except:
        print("Error converting text to speech")
        return None
    
def upload_to_s3(bucket_name: str, write_file: str, key: str):
    """
    Uploads audio file to S3 bucket
    """
    try:
        with open(write_file, 'rb') as file:
            write_file = s3_client.put_object(
            Bucket = bucket_name,
            key = key,
            body = file
            )
        return write_file
    except Exception as e:
        print(f'"{e}Error uploading to S3", e')

def main():
    convert_text_to_speech(input_text_file_path="speech.txt", converted_file=converted_file)
    upload_to_s3(bucket_name="polly-demo-2025-luit-jun10", converted_file=converted_file, key="audio/"+str(datetime.now())+".mp3") 


if __name__ == "__main__":
    main()
        
    


        