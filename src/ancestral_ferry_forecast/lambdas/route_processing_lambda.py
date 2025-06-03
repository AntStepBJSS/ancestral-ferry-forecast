import json

import boto3
from datetime import datetime

from pydantic import BaseModel
from pydantic import ValidationError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("hackathon-ancestral-route-data-db")

class PointData(BaseModel):
    lat: float
    lon: float

class RequestModel(BaseModel):
    route_id: str
    start_datetime: datetime
    end_datetime: datetime
    points: list[PointData]

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))
        request = RequestModel.model_validate(body)

        response = table.get_item(Key={"route_id": request.route_id})
        route_item = response.get("Item")

        if not route_item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Route {request.route_id} not found."})
            }

        result = {}

        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except ValidationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid input", "details": e.errors()})
        }
