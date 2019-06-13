#!/usr/bin/python

import sys
import signal
import random
import boto3
import time
import json
import uuid

StreamName = 'KinesisStream'

def InterruptHandler(signal, frame):
    print
    sys.exit(0)

signal.signal(signal.SIGINT, InterruptHandler)
random.seed()

Kinesis = boto3.client('kinesis')
SourceData  = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890'
Counter = 0

while True:
    try:
        UUID = str(uuid.uuid4())
        
        Data = {}
        Data['Id']      = UUID
        Data['Field01'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field02'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field03'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field04'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field05'] = ''.join(random.choice(SourceData) for _ in range(16))
        Data['Field06'] = ''.join(random.choice(SourceData) for _ in range(16))
        
        print('Sending message %d (%s)' % (Counter,UUID))
       
        Response = Kinesis.put_record(StreamName=StreamName, PartitionKey=UUID, Data=json.dumps(Data))
    except Exception as e:
        print('Kinesis put failed: %s' % str(e))

    time.sleep(0.1)
    Counter += 1
