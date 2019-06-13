#!/usr/bin/python

import sys
import signal
import boto3

SQSQueueUrl = '<SQS Queue URL>'

def InterruptHandler(signal, frame):
    print
    sys.exit(0)

signal.signal(signal.SIGINT, InterruptHandler)

SQS = boto3.client('sqs')

while True:
    try:
        Response = SQS.receive_message(QueueUrl=SQSQueueUrl, MaxNumberOfMessages=10, WaitTimeSeconds=5)
    except Exception as e:
        print('SQS receive failed: %s' % str(e))
        continue
    
    if 'Messages' not in Response:
        print('No messages in queue')
        continue

    for Messages in Response['Messages']:
        Handle = Messages['ReceiptHandle']
        Message = Messages['Body']

        print('Received: %s' % Message)

        try:
            Response = SQS.delete_message(QueueUrl=SQSQueueUrl, ReceiptHandle=Handle)
        except Exception as e:
            print('SQS delete failed: %s' % str(e))
