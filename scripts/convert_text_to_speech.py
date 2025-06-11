#!/usr/bin/env python3
"""
Text-to-Speech Synthesis Script using Amazon Polly
Converts text files to MP3 audio and uploads to S3
"""

import boto3
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional


def convert_text_to_speech(file_path: str, voice_id: str = 'Joanna') -> Optional[Dict]:
    """
    Convert a text file to speech using Amazon Polly and upload to S3
    
    Args:
        file_path: Path to the text file
        voice_id: Amazon Polly voice ID to use
        
    Returns:
        Dictionary with conversion results or None if failed
    """
    # Initialize AWS clients
    polly = boto3.client('polly', region_name=os.environ['AWS_REGION'])
    s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'])
    
    try:
        # Read text file
        with open(file_path, 'r') as f:
            text = f.read()
        
        if not text:
            print(f"Warning: {file_path} is empty, skipping...")
            return None
                
        print(f"Converting {file_path} to speech using voice: {voice_id}")
        print(f"Text length: {len(text)} characters")
        
        # Generate speech using Amazon Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id
        )
        
        # Generate output filename with timestamp
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"{base_name}_{voice_id}_{timestamp}.mp3"
        
        # Upload to S3
        bucket_name = os.environ['S3_BUCKET']
        s3_key = f"audio/{audio_filename}"
        
        # Read audio stream and upload to S3
        audio_data = response['AudioStream'].read()
        
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=audio_data,
            ContentType='audio/mpeg',
            Metadata={
                'source-file': file_path,
                'voice-id': voice_id,
                'generated-at': datetime.now().isoformat(),
                'commit-sha': os.environ.get('GITHUB_SHA', 'unknown'),
                'original-char-count': str(original_length),
                'processed-char-count': str(len(text))
            }
        )
        
        # Generate URLs
        s3_url = f"https://{bucket_name}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{s3_key}"
        
        print(f"✅ Successfully converted {file_path}")
        print(f"   Audio saved to: s3://{bucket_name}/{s3_key}")
        print(f"   Public URL: {s3_url}")
        print(f"   Audio file size: {len(audio_data)} bytes")
        
        # Return metadata for summary
        return {
            'source_file': file_path,
            'audio_file': audio_filename,
            's3_key': s3_key,
            's3_url': s3_url,
            'voice_id': voice_id,
            'character_count': len(text),
            'original_character_count': original_length,
            'audio_size_bytes': len(audio_data),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error converting {file_path}: {str(e)}")
        # Print more detailed error info for debugging
        if hasattr(e, 'response'):
            print(f"   AWS Error Code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
            print(f"   AWS Error Message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        return None


def validate_environment() -> bool:
    """
    Validate that required environment variables are set
    
    Returns:
        True if environment is valid, False otherwise
    """
    required_vars = ['AWS_REGION', 'S3_BUCKET']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def validate_aws_permissions():
    """
    Test AWS permissions for Polly and S3
    """
    try:
        # Test Polly access
        polly = boto3.client('polly', region_name=os.environ['AWS_REGION'])
        polly.describe_voices(MaxItems=1)
        print("✅ Amazon Polly access confirmed")
        
        # Test S3 access
        s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'])
        bucket_name = os.environ['S3_BUCKET']
        s3.head_bucket(Bucket=bucket_name)
        print(f"✅ S3 bucket access confirmed: {bucket_name}")
        
    except Exception as e:
        print(f"❌ AWS permission error: {str(e)}")
        sys.exit(1)


def main():
    """
    Main execution function
    """
    # Validate command line arguments
    if len(sys.argv) < 2:
        print("Usage: python synthesize.py <file1> [file2] ... [voice_id]")
        print("Example: python synthesize.py texts/hello.txt texts/world.txt Joanna")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    voice_id = 'Joanna'  # Default voice
    
    # Check if last argument is a voice ID (not a file path)
    if args and not args[-1].endswith('.txt') and '/' not in args[-1]:
        voice_id = args[-1]
        file_paths = args[:-1]
    else:
        file_paths = args
    
    # Handle space-separated file list (from GitHub Actions)
    if len(file_paths) == 1 and ' ' in file_paths[0]:
        file_paths = file_paths[0].split()
    
    # Filter out empty strings
    file_paths = [f for f in file_paths if f.strip()]
    
    if not file_paths:
        print("No valid file paths provided")
        sys.exit(1)
    
    print(f"🎵 Starting Text-to-Speech conversion")
    print(f"   Files to process: {len(file_paths)}")
    print(f"   Voice: {voice_id}")
    print(f"   AWS Region: {os.environ.get('AWS_REGION', 'Not set')}")
    print(f"   S3 Bucket: {os.environ.get('S3_BUCKET', 'Not set')}")
    print()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Validate AWS permissions
    validate_aws_permissions()
    print()
    
    # Process each file
    results = []
    for file_path in file_paths:
        file_path = file_path.strip()
        if file_path and os.path.exists(file_path):
            print(f"Processing: {file_path}")
            result = convert_text_to_speech(file_path, voice_id)
            if result:
                results.append(result)
            print()  # Add spacing between files
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Save results for GitHub Actions summary
    if results:
        with open('conversion_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    # Print final summary
    print("📊 Conversion Summary:")
    print(f"   Files processed: {len(results)}")
    print(f"   Voice used: {voice_id}")
    print(f"   S3 bucket: {os.environ.get('S3_BUCKET')}")
    
    if results:
        total_chars = sum(r['character_count'] for r in results)
        total_size = sum(r['audio_size_bytes'] for r in results)
        print(f"   Total characters: {total_chars:,}")
        print(f"   Total audio size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    print(f"   Results saved to: conversion_results.json")


if __name__ == '__main__':
    main()