#!/usr/bin/python

import sys
import signal
import boto3
import time
import json

StreamName = 'KinesisStream'

def InterruptHandler(signal, frame):
    print
    sys.exit(0)

signal.signal(signal.SIGINT, InterruptHandler)

Kinesis = boto3.client('kinesis')
Counter = 0

while True:
    try:
        Response = Kinesis.describe_stream(StreamName=StreamName)
        ShardId  = Response['StreamDescription']['Shards'][0]['ShardId']
    except Exception as e:
        print('Kinesis setup failed: %s' % str(e))
        sys.exit(1)
        
    Iterator   = Kinesis.get_shard_iterator(StreamName=StreamName, ShardId=ShardId, ShardIteratorType='LATEST')
    MyIterator = Iterator['ShardIterator']
    Record = {}
    Record['NextShardIterator'] = MyIterator

    Counter = 0
    while True:
        Data = Kinesis.get_records(ShardIterator = Record['NextShardIterator'], Limit=20)
        if len(Data['Records']) > 0: break
        time.sleep(1)
        Counter += 1
        if Counter > 250: # The shard iterator has a timeout of 300 seconds
            data['Ignore'] = True # So we don't throw an error below
            break

    if Data.has_key('Ignore'): continue

    for Record in Data['Records']:
        Payload = json.loads(Record["Data"])
        print(Payload)
