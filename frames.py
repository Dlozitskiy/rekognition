from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib
import os

print('Loading function')

rekognition = boto3.client('rekognition')
s3 = boto3.resource('s3')

# --------------- Helper Functions to call Rekognition APIs ------------------

def detect_faces(bucket, key):
    response = rekognition.detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return response

def lambda_handler(event, context):
    bucket = s3.Bucket(os.environ['s3bucket']) 
    interval = 0
    array={}
    for object in bucket.objects.filter(Prefix=os.environ['s3prefix']):
        response = detect_faces(bucket.name, object.key)
        s3.Object(bucket.name,object.key).delete()
        count = 0
        for faces in response['FaceDetails']:
            count += 1
        array[interval] = count
        interval = interval + int(os.environ['interval'])
        interval_list = []
        count_list = []
        for i in array:
            interval_list.append(i)
            count_list.append(array[i])
    bucket.put_object(
    Bucket=os.environ['s3bucket'],
    Key='meta/results.html',
    ContentType='text/html',
    Body=b'<!DOCTYPE html>\
    <html>\
    <head>\
    <script src="https://sdk.amazonaws.com/js/aws-sdk-2.224.1.min.js">\
    </script>\
    <script src="../app.js">\
    </script>\
    <script src="https://cdn.plot.ly/plotly-latest.min.js">\
    </script>\
    <script>deleteResult();\
    </script>\
    <style>\
    html {text-align: center;}\
    </style>\
    </head>\
    <body>\
    <h1>Number of people in a video frame every '+str(os.environ['interval'])+' second:</h1>\
    <div id="myDiv"></div>\
    <script>\
    var trace1 = {\
      x: '+str(interval_list)+',\
      y: '+str(count_list)+',\
      mode: \'markers\',\
      marker: {\
        color: \'rgb(219, 64, 82)\',\
        size: 12\
      }\
    };\
    var data = [trace1];\
    var layout = {\
      xaxis: {\
        title: \'Seconds\',\
      },\
      yaxis: {\
        title: \'People\',\
      }\
    };\
    Plotly.newPlot(\'myDiv\', data, layout, {yaxis: {dtick: 1}, xaxis: { tickformat: ",d" }});\
    </script>\
    </body>\
    </html>')