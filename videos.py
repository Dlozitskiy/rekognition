from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib
import os

print('Loading function')

rekognition = boto3.client('rekognition')
elastictranscoder = boto3.client('elastictranscoder')

def detect_faces(bucket, key):
    response = rekognition.start_face_detection(
        Video={"S3Object": {"Bucket": bucket, "Name": key}},
        NotificationChannel={
        'SNSTopicArn': os.environ['SNSTopicArn'],
        'RoleArn': os.environ['RoleArn']
        })
    return response

def ets_create_job(key):
    response = elastictranscoder.create_job(
        PipelineId=os.environ['PipelineId'],
        Input={'Key': key},
        OutputKeyPrefix='thumbnails/',
        Output={
        'Key': 'transcoded-video.mp4',
        'ThumbnailPattern': 'thumbnail-{count}',
        'PresetId': os.environ['PresetId']
        })    
    return response

# --------------- Main handler ------------------

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        
        if 'video' in key:
            # Calls rekognition DetectFaces API to detect faces in S3 object
            response = detect_faces(bucket, key)
            # Print response to console.
            print(response)
            return response
        elif 'frames' in key:
            response = ets_create_job(key)
            
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
