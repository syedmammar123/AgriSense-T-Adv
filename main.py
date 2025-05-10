import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any, Union
import json
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
import logging
from generate_tasks import generate_farm_tasks
from weekly_advisory import generate_weekly_advisory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Import our farm_analyzer module
from farm_analyzer import generate_farm_report
from weather_service import get_weather

app = FastAPI(title="Farm Analysis API", description="API for analyzing farm images")


class FarmParameters(BaseModel):
    crop: Optional[str] = ""
    farmLocation: Optional[str] = ""
    currentGrowthStage: Optional[str] = ""
    soilType: Optional[str] = ""
    sowingDate: Optional[str] = ""
    irrigationType: Optional[str] = ""
    waterAvailabilityStatus: Optional[str] = ""
    waterSource: Optional[str] = ""
    fertilizersUsed: Optional[str] = ""
    currentWeather: Optional[str] = ""


class FarmAnalysisRequest(BaseModel):
    image_urls: List[str] = Field(..., description="List of image URLs to analyze")
    parameters: FarmParameters = Field(..., description="Farm parameters")


class PreviousTask(BaseModel):
    taskId: str
    title: str
    priority: str
    dueDate: str
    status: str
    context: Optional[str] = None
    taskDescription: Optional[str] = None
    steps: Optional[List[str]] = None
    supportingInformation: Optional[str] = None
    followUp: Optional[str] = None
    dependencies: Optional[List[str]] = None


class FarmTaskRequest(BaseModel):
    parameters: FarmParameters = Field(..., description="Farm parameters")
    farm_report: str = Field(..., description="Farm report text")
    previous_tasks: Union[str, List[PreviousTask], None] = Field(
        None, description="Previous farm tasks as JSON string or object"
    )

    @validator("previous_tasks")
    def validate_previous_tasks(cls, value):
        # Handling JSON string
        if isinstance(value, str):
            try:
                # Try to parse the JSON string
                parsed_data = json.loads(value)
                # Ensure it's a list
                if not isinstance(parsed_data, list):
                    raise ValueError("JSON string must decode to a list")
                return value  # Keep as string for processing
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string for previous_tasks")
        return value  


class FarmAdvisoryRequest(BaseModel):
    parameters: FarmParameters = Field(..., description="Farm parameters")
    farm_report: str = Field(..., description="Farm report text")
    upcoming_tasks: Union[str, List[PreviousTask], None] = Field(
        None, description="Upcoming farm tasks as JSON string or object"
    )
    weather_data: Optional[Any] = None

    @validator("upcoming_tasks")
    def validate_upcoming_tasks(cls, value):
        # Handle JSON string
        if isinstance(value, str):
            try:
                # Try to parse the JSON string
                parsed_data = json.loads(value)
                # Ensure it's a list
                if not isinstance(parsed_data, list):
                    raise ValueError("JSON string must decode to a list")
                return value  # Keep as string for processing
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string for upcoming_tasks")
        return value  # Return as is if already a list or None


@app.post("/generate-report")
async def analyze_farm(request: FarmAnalysisRequest):
    logger.info(f"Received request with {len(request.image_urls)} images")
    logger.info(f"Parameters: {request.parameters.dict()}")
    """
    Analyze farm images from URLs and generate a report
    """
    if not request.image_urls:
        raise HTTPException(status_code=400, detail="No image URLs provided")

    try:
        # Convert parameters to dictionary
        params = request.parameters.dict()

        # If farmLocation is provided, get the current weather
        if params.get("farmLocation"):
            try:
                weather_data = get_weather(params["farmLocation"], 1)
                if isinstance(weather_data, dict) and "error" not in weather_data:
                    first_date = next(iter(weather_data))
                    weather_info = weather_data[first_date]
                    params["currentWeather"] = (
                        f"{weather_info['Condition']}, {weather_info['Max Temp']}, {weather_info['Humidity']} humidity"
                    )
            except Exception as e:
                logger.error(f"Failed to fetch weather: {str(e)}")

        logger.info(f"Current weather: {params.get('currentWeather', 'Not available')}")

        # Generate report using the URLs and updated parameters
        report = generate_farm_report(request.image_urls, params)

        # Try to parse the report as JSON
        try:
            report_data = json.loads(report)
            return report_data
        except json.JSONDecodeError:
            # If it's not valid JSON, return as text
            return {"report": report}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.post("/create-tasks")
async def create_tasks(request: FarmTaskRequest):
    """
    Generate tasks for farm based on farm report and parameters.
    """
    logger.info(f"Received task creation request")
    logger.info(f"Parameters: {request.parameters.dict()}")
    logger.info(f"Report: {request.farm_report}")
    logger.info(f"Previous Tasks: {request.previous_tasks}")

    try:
        # Convert parameters to dictionary
        params = request.parameters.dict(exclude_none=True)
        weather_data = None

        # If farmLocation is provided, get the weather forecast for the next 7 days
        if params.get("farmLocation"):
            try:
                weather_data = get_weather(
                    params["farmLocation"], 10
                )  
                if isinstance(weather_data, dict) and "error" not in weather_data:
                    # Format the weather data as a string
                    weather_str = ""
                    for date, info in weather_data.items():
                        weather_str += f"\n  {date}\n"
                        for key, value in info.items():
                            weather_str += f"  {key}: {value}\n"

                    params["currentWeather"] = weather_str
            except Exception as e:
                logger.error(f"Failed to fetch weather forecast: {str(e)}")

        # Handle previous_tasks - it can now be a JSON string or a list
        previous_tasks = request.previous_tasks
        if isinstance(previous_tasks, str):
            try:
                # If it's a JSON string, parse it
                previous_tasks_list = json.loads(previous_tasks)
                params["previousTasks"] = previous_tasks_list
            except json.JSONDecodeError:
                logger.error("Failed to parse previous_tasks JSON string")
        elif previous_tasks:
            # If it's already a list of objects
            params["previousTasks"] = [
                task.dict(exclude_none=True) for task in previous_tasks
            ]

        # Generate tasks based on parameters and farm report
        tasks_json = generate_farm_tasks(
            parameters=params, farm_report=request.farm_report
        )

        # Parse the JSON response
        try:
            tasks_data = (
                json.loads(tasks_json) if isinstance(tasks_json, str) else tasks_json
            )

            response = {"tasks": tasks_data, "weather": weather_data}
            return response
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return {"error": "Failed to parse tasks", "raw_response": tasks_json}

    except Exception as e:
        logger.error(f"Error in create_tasks: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.post("/create-advisory")
async def create_advisory(request: FarmAdvisoryRequest):
    """
    Generate weekly advisory based on farm report, parameters, and upcoming tasks.
    """
    logger.info(f"Received Advisory creation request")
    logger.info(f"Parameters: {request.parameters.dict()}")
    logger.info(f"Report: {request.farm_report}")
    logger.info(f"Upcoming Tasks: {request.upcoming_tasks}")
    logger.info(f"Weather Data: {request.weather_data}")

    try:
        # Convert parameters to dictionary
        params = request.parameters.dict(exclude_none=True)

        # Handle upcoming_tasks - it can now be a JSON string or a list
        upcoming_tasks = request.upcoming_tasks
        if isinstance(upcoming_tasks, str):
            try:
                # If it's a JSON string, parse it
                upcoming_tasks_list = json.loads(upcoming_tasks)
                params["upcomingTasks"] = upcoming_tasks_list
            except json.JSONDecodeError:
                logger.error("Failed to parse upcoming_tasks JSON string")
        elif upcoming_tasks:
            # If it's already a list of objects
            params["upcomingTasks"] = [
                task.dict(exclude_none=True) for task in upcoming_tasks
            ]

        advisory_data_json = generate_weekly_advisory(
            parameters=params,
            farm_report=request.farm_report,
            farm_tasks_for_upcoming_week=params.get("upcomingTasks", []),
            weather_data=request.weather_data,
        )

        # Parse the JSON response
        try:
            advisory_data = (
                json.loads(advisory_data_json)
                if isinstance(advisory_data_json, str)
                else advisory_data_json
            )

            return advisory_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return {
                "error": "Failed to parse advisory data",
                "raw_response": advisory_data_json,
            }

    except Exception as e:
        logger.error(f"Error in create_advisory: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@app.get("/weather")
async def get_location_weather(location: str, days: int = 1):
    """
    Get weather forecast for a specific location
    """
    if not location:
        raise HTTPException(status_code=400, detail="Location parameter is required")

    try:
        weather_data = get_weather(location, days)
        if "error" in weather_data:
            raise HTTPException(status_code=400, detail=weather_data["error"])
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Welcome to AgriSense FastAPI"}


if __name__ == "__main__":
    import uvicorn

    # Get port and host from environment variables with defaults
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
