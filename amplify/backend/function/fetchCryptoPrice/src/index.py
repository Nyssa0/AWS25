import json
import os
import boto3
import requests
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
table_name = os.environ.get('STORAGE_CRYPTOPRICES_NAME')
table = dynamodb.Table(table_name)

def handler(event, context):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&page=1"
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)
        data = response.json()

        if not data:
            return response_obj(404, {"error": "No data received from the API"})

        inserted_items = []

        for crypto in data:
            item = {
                "crypto_id": crypto["id"],  # ex: 'bitcoin'
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": crypto["symbol"].upper(),
                "name": crypto["name"],
                "price_usd": Decimal(str(crypto["current_price"]))
            }

            table.put_item(Item=item)
            inserted_items.append(item["crypto_id"])

        return response_obj(200, {
            "message": f"{len(inserted_items)} crypto data saved.",
            "inserted_ids": inserted_items
        })
    except Exception as e:
        return response_obj(500, {"error": str(e)})

def response_obj(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }