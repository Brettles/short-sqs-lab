#!/usr/bin/python

import sys
import signal
import random
import boto3
import time
import json

SQSQueueUrl = '<SQS Queue URL>'

def InterruptHandler(signal, frame):
    print
    sys.exit(0)

signal.signal(signal.SIGINT, InterruptHandler)
random.seed()

SQS = boto3.client('sqs')
SourceData  = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890'
Counter = 0

while True:
    try:
        Data = {}
        Data['Message'] = Counter
        Data['Field01'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field02'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field03'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field04'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field05'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field06'] = ''.join(random.choice(SourceData) for _ in range(16))
        
        print('Sending message %d' % Counter)
       
        Response = SQS.send_message(QueueUrl=SQSQueueUrl,
                                    MessageBody=json.dumps(Data),
                                    MessageGroupId='Group1')
    except Exception as e:
        print('SQS send failed: %s' % str(e))

    time.sleep(0.1)
    Counter += 1
