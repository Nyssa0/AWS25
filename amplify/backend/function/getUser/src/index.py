import json
import os
import boto3

dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")
table_name = os.environ.get("STORAGE_USERS_NAME")
table = dynamodb.Table(table_name)

def handler(event, context):
    if event.get("httpMethod") != "GET":
        return response(405, {"error": "Unauthorized method, use GET."})

    params = event.get("queryStringParameters") or {}

    user_id = params.get("id")
    email = params.get("email")

    if user_id:
        return get_user_by_id(user_id)
    elif email:
        return get_user_by_email(email)
    else:
        return response(400, {"error": "Provide an id or an email."})


def get_user_by_id(user_id):
    try:
        result = table.get_item(Key={"id": user_id})
        item = result.get("Item")
        if item:
            return response(200, item)
        else:
            return response(404, {"error": "User not found."})
    except Exception as e:
        return response(500, {"error": f"Server error : {str(e)}"})


def get_user_by_email(email):
    try:
        result = table.query(
            IndexName="email-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("email").eq(email)
        )
        items = result.get("Items", [])
        if items:
            return response(200, items[0])
        else:
            return response(404, {"error": "User not found with this email."})
    except Exception as e:
        return response(500, {"error": f"Server error : {str(e)}"})


def response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        "body": json.dumps(body_dict)
    }