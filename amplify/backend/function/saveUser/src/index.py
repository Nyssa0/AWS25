import json
import os
import uuid
import boto3
import re

dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
table_name = os.environ.get('STORAGE_USERS_NAME')
table = dynamodb.Table(table_name)
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def handler(event, context):
    if event.get('httpMethod') != 'POST':
        return response(405, {"error": "Unauthorized method, use POST."})

    try:
        body = json.loads(event['body'])
    except (json.JSONDecodeError, TypeError):
        return response(400, {"error": "Invalid body request."})

    name = body.get('name', '').strip()
    email = body.get('email', '').strip()

    if not name or not email:
        return response(400, {"error": "'name' and 'email' fields are required."})

    if not EMAIL_REGEX.match(email):
        return response(400, {"error": "Invalid email format."})

    existing_user = get_user_by_email(email)
    if existing_user:
        return response(409, {"error": "Email already used."})

    new_user = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
    }

    table.put_item(Item=new_user)

    return response(201, {"message": "User created successfully.", "user": new_user})

def get_user_by_email(email):
    response = table.scan(
        FilterExpression="email = :email",
        ExpressionAttributeValues={":email": email}
    )
    items = response.get("Items", [])
    return items[0] if items else None

def response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps(body_dict)
    }