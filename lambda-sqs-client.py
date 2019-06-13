import json

def lambda_handler(event, context):
    for Record in event['Records']:
        print(Record['body'])
        
    return {
        'statusCode': 200
    }

