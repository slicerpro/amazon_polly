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

def convert_text_to_speech(input_text_file_path: str):
    """
    Converts text to speech using Amazon Polly
    """
    try:
        with open(input_text_file_path, 'r') as file: 
            text = file.read()
            output_file = polly_client.synthesize_speech(
                Text=text,
                OutPutFormat='mp3',
                VoiceId='Joanna'
            )
        return output_file
    except:
        print("Error converting text to speech")
        return None
    
def upload_to_s3(bucket_name: str, output_file: str,key: str):
        """
    Uploads audio file to S3 bucket
    """
try:
        with open(output_file, 'wb') as file:
            write_file = s3_client.put_object(
            bucket = bucket_name,
            key = key,
            body = file
            )
except Exception as e:
        print(f'"{e}Error uploading to S3", e')
        

if __name__ == "__main__":
      convert_text_to_speech(sys.argv[0])
      upload_to_s3   
    


        