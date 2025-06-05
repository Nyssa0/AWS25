import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
s3 = boto3.client('s3')

table_name = os.environ.get('STORAGE_CRYPTO_NAME')
bucket_name = os.environ.get('STORAGE_CRYPTOFILESSTORAGE_BUCKETNAME')

table = dynamodb.Table(table_name)

def handler(event, context):
    if event.get("httpMethod") != "GET":
        return response_obj(405, {"error": "Unauthorized method. Use GET."})

    try:
        response = table.scan()
        items = response.get("Items", [])

        if not items:
            return response_obj(404, {"error": "No data found in DynamoDB"})

        json_ready_data = json.loads(json.dumps(items, default=decimal_handler))

        file_name = f"crypto_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.json"

        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(json_ready_data),
            ContentType='application/json'
        )

        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name
            },
            ExpiresIn=3600  # en secondes = 1h
        )

        return response_obj(200, {
            "message": f"File {file_name} generated on S3.",
            "url": presigned_url
        })

    except Exception as e:
        return response_obj(500, {"error": str(e)})

def response_obj(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }

def decimal_handler(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError