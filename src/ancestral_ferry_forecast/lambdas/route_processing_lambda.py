import json
import logging
import os
from typing import Optional

import dacite
from dacite import from_dict

import boto3
from datetime import datetime
from dataclasses import dataclass
from dateutil.parser import isoparse

# V1
# {
#  "body": {
#    "latitude": 51.7,
#    "longitude": -1.1,
#  }
# }
# V2
# {
#  "body": {
#    "route_id": "Portsmouth - Fishbourne",
#    "start_datetime": "2025-06-03T15:30:00Z",
#    "end_datetime": "2025-06-03T16:30:00Z",
#    "points": [{
#            "lat": 51.1,
#            "lon": -1.1
#            "unsafe_wind_direction": 100-110
#            "datetime": "2025-06-03T15:45:00Z",
#       },{
#            "lat": 51.2,
#            "lon": -1.2
#            "unsafe_wind_direction": 110-120
#            "datetime": "2025-06-03T16:00:00Z",
#        }]
#  }
# }


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("hackathon-ancestral-route-data-db")
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger = logging.getLogger()
logger.setLevel(log_level)


@dataclass
class PointData:
    lat: float
    lon: float
    datetime: datetime
    unsafe_wind_direction: Optional[str] = None  # 170-200,350-20


@dataclass
class RequestModelV1:
    latitude: float
    longitude: float
    datetime: datetime


@dataclass
class RequestModelV2:
    route_id: str
    start_datetime: datetime
    end_datetime: datetime
    points: list[PointData]


@dataclass
class Location:
    latitude: float  # 50.7463
    longitude: float  # -1.1808
    name: str  # Fishbourne
    un_locode: str  # GBRYD


@dataclass
class Route:
    route_name: str  # Portsmouth - Fishbourne
    start: Location
    end: Location
    notes: str  # Sheltered in the Solent; vulnerable to strong SW or N winds.
    unsafe_wind_direction: str  # 170-200,350-20
    vessel_type: Optional[str] = None  # RORO Ferry
    operator: Optional[str] = None


def lambda_handler(event, context):
    try:
        logger.info(f"event is {event['body']}")
        body = event['body']
        # always expecting a dict here, could be V1 or V2
        if body.get("latitude") is not None:
            # it's V1
            request = RequestModelV1(**body)
            return [request]

        # Guess it's V2 then
        request = from_dict(
            data_class=RequestModelV2,
            data=body,
            config=dacite.Config(type_hooks={datetime: isoparse})
        )

        ddb_response = table.get_item(Key={"route_name": request.route_id})
        route_item = ddb_response.get("Item")
        if not route_item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Route {request.route_id} not found."})
            }
        route = Route(**route_item)
        logger.info(f"route is {route}")

        result = [route.start]
        logger.info(f"created result {result}")

        for point in request.points:
            logger.info(f"traversing point {point}")
            logger.info(f" point.lat is {point.lat}")

            # copying here as there's a question over lat/lon latitude/longitude naming atm, plus it
            # doesn't hurt to leave the original unmutated
            data_point = PointData(
                lat = point.lat,
                lon = point.lon,
                unsafe_wind_direction = point.unsafe_wind_direction,
                datetime = point.datetime)
            result.append(data_point)

        result.append(route.end)

        return result
    except Exception as e:
        return {
            "statusCode": 400,
            "body": str(e)
        }
