"""
Text-to-Speech Conversion Script for CI/CD Pipeline

This script converts text files to audio using Amazon Polly and uploads
the resulting audio files to Amazon S3. It's designed to be used in a 
GitHub Actions CI/CD pipeline but can also be run standalone.

Requirements:
    - boto3: AWS SDK for Python
    - AWS credentials configured (via environment variables or AWS config)
    - S3_BUCKET_NAME environment variable set

Example:
    python convert_text_to_speech.py input.txt
    python convert_text_to_speech.py input.txt custom/output/path.mp3

Author: CI/CD Pipeline
Version: 1.0
"""

import boto3
import os
import sys
from pathlib import Path
import json


def convert_text_to_speech(text_file_path, output_key=None):
    """
    Convert a text file to speech using Amazon Polly and upload to S3.
    
    This function reads a text file, converts it to speech using Amazon Polly and uploads the resulting MP3 file to an S3 bucket.
    
    Args:
        text_file_path (str): Path to the input text file to be converted.
        output_key (str, optional): S3 key (path) where the audio file will be stored.
                                   If not provided, defaults to 'audio/{filename}.mp3'.
    
    Returns:
        bool: True if conversion and upload were successful, False otherwise.
    
    Raises:
        FileNotFoundError: If the input text file cannot be found.
        Exception: For AWS-related errors (Polly or S3 failures).
    
    Environment Variables:
        S3_BUCKET_NAME (str): Name of the S3 bucket where audio files will be stored.
    
    Example:
        >>> success = convert_text_to_speech('sample.txt', 'audio/sample.mp3')
        >>> if success:
        ...     print("Conversion completed successfully!")
    """
    # Initialize AWS clients
    polly_client = boto3.client('polly')
    s3_client = boto3.client('s3')

    output_key = 'audio-files/output.mp3'
    
    # Read text file
    try:
        with open(text_file_path, 'r') as file:
            text_content = file.read()
    except FileNotFoundError:
        print(f"Error: Text file '{text_file_path}' not found")
        return False
    
    # Convert text to speech
    try:
        response = polly_client.synthesize_speech(
            Text=text_content,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        
        # Upload to S3
        s3_client.put_object(
            Bucket=os.environ['S3_BUCKET_NAME'],
            Key=output_key,
            Body=response['AudioStream'].read(),
            ContentType='audio/mpeg'
        )
        
        print(f"Successfully converted '{text_file_path}' to audio and uploaded to S3: {output_key}")
        return True
        
    except Exception as e:
        print(f"Error converting text to speech: {str(e)}")
        return False


def main():
    """
    Main function to handle command-line execution of the text-to-speech converter.
    
    This function parses command-line arguments and calls the convert_text_to_speech function with the appropriate parameters. It handles basic argument validation and exits with appropriate status codes.
    
    Command-line Arguments:
        text_file_path (str): Required. Path to the text file to convert.
        output_key (str): Optional. Custom S3 key for the output audio file.
    
    Exit Codes:
        0: Success - conversion completed without errors
        1: Failure - conversion failed or invalid arguments
    
    Usage:
        python convert_text_to_speech.py <text_file_path> [output_key]
    
    Examples:
        python convert_text_to_speech.py speech.txt
        python convert_text_to_speech.py speech.txt custom/path/audio.mp3
    """
    if len(sys.argv) < 2:
        print("Usage: python convert_text_to_speech.py <text_file_path> [output_key]")
        sys.exit(1)
    
    text_file_path = sys.argv[1]
    output_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_text_to_speech(text_file_path, output_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()