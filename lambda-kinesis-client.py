import json
import base64

def lambda_handler(event, context):
    for Record in event['Records']:
        Data = json.loads(base64.b64decode(Record['kinesis']['data']))
        print(Data)
        
    return {
        'statusCode': 200
    }

