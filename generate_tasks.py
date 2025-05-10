import os
import json
from groq import Groq
from datetime import datetime

EXAMPLE_TASK = [
    {
        "taskId": "T-2025-04-W17-01",
        "title": "Optimize Irrigation Schedule for Hot Weather",
        "priority": "High",
        "dueDate": "2025-04-24",
        "status": "Not Started",
        "context": "With forecasted temperatures reaching 35-40°C and humidity at 14-16%, the wheat crop in tillering stage is at risk of moisture stress. Current moisture level is Low with limited water availability from groundwater source using drip irrigation.",
        "taskDescription": "Adjust the irrigation schedule to provide adequate moisture during the critical tillering stage while conserving limited water resources. Proper irrigation management during this period is essential for tiller development and will directly impact final yield. The current dry conditions combined with rising temperatures create a high risk of water stress that could permanently reduce the crop's yield potential.",
        "steps": [
            "Inspect the existing drip irrigation system for any clogs or damage",
            "Increase irrigation frequency from once per day to twice daily (early morning and evening)",
            " Reduce each irrigation session duration by 15% to conserve water while maintaining soil moisture",
            "Focus additional water on areas that show signs of stress (wilting or yellowing)",
            "Monitor soil moisture daily by checking 4-6 inches below surface",
        ],
        "supportingInformation": "Research shows that wheat yield can decrease by up to 50% when moisture stress occurs during the tillering stage. Optimizing irrigation during this period is critical for developing a strong root system and healthy tillers that will support grain development. The current tillering stage represents a critical period where water management directly impacts final yield potential.",
        "followUp": "Check soil moisture levels daily and observe plant vigor. Adjust irrigation schedule if conditions change or if plants show signs of continued stress despite irrigation adjustments.",
        "dependencies": [
            "Requires completion of Task T-2025-04-W16-01 (Irrigation System Maintenance)",
            "Requires stable electricity supply for pump operation",
        ],
    }
]


def generate_farm_tasks(parameters, farm_report, example_tasks=EXAMPLE_TASK):
    """
    Generate weekly farm tasks based on farm report, parameters, and previous tasks status
    with enhanced features for dependencies.

    Args:
        parameters: Dictionary containing farm parameters (crop, location, soil type, etc.)
        farm_report: String containing the latest farm condition report
        example_tasks: Example tasks to guide the LLM (optional)

    Returns:
        JSON formatted tasks for the upcoming week
    """

    dependencies_guidance = """
    Tasks should include dependency information when applicable. Dependencies should be listed in the "dependencies" field and can reference:
    1. Previous tasks that must be completed first
    2. Conditions that must be met before task execution
    3. Resources that must be available

    For example:
    ```
    "dependencies": [
      "Requires completion of Task T-2025-04-W17-01 (Irrigation System Maintenance)",
      "Requires soil moisture level at Medium or higher",
      "Requires clear weather with minimal wind"
    ]
    ```
    """

    task_prompt = f"""
    I need to generate comprehensive weekly farm tasks for a {parameters.get('crop', '')} farm in {parameters.get('farmLocation', '')}.

    ## FARM REPORT (Generated on {datetime.now().strftime('%Y-%m-%d')}):
    {farm_report}

    ## FARM PARAMETERS:
    - Crop: {parameters.get('crop', '')}
    - Location: {parameters.get('farmLocation', '')}
    - Growth Stage: {parameters.get('currentGrowthStage', '')}
    - Soil Type: {parameters.get('soilType', '')}
    - Irrigation Type: {parameters.get('irrigationType', '')}
    - Water Availability: {parameters.get('waterAvailabilityStatus', '')}
    - Fertilizer Type: {parameters.get('fertilizersUsed', '')}

    ## WEATHER FORECAST (Next 7 days):
    {parameters.get('currentWeather', 'No weather data available')}



    ## PREVIOUS WEEK'S TASKS STATUS:
    {parameters.get('previousTasks', 'This is the first week of task generation, no previous tasks available')}
    

    {dependencies_guidance}

    Based on all the above information, generate 4-5 comprehensive agricultural tasks for the upcoming week. The tasks should be actionable, specific to the current farm conditions, prioritized appropriately, and incorporate local farming knowledge and practices from {parameters.get('farmLocation', '')}.

    Each task should include:
    1. A unique task ID (format: T-YYYY-MM-W##-##)
    2. A clear, action-oriented title
    3. Priority level (High/Medium/Low)
    4. Due date or timeframe (specific days within the upcoming week)
    5. Initial status (always "Not Started")
    6. Detailed context relevant to the task
    7. A very comprehensive and detailed task description explaining what needs to be done and why. It has to be a complete paragraph.
    8. Detailed step-by-step instructions on how to complete the task
    9. Supporting information explaining the importance and benefits
    10. Follow-up actions after task completion
    11. Dependencies on other tasks or conditions

    If any previous tasks were not completed or marked as "In Progress", incorporate them into this week's tasks with appropriate priority adjustments if they are still relevant.

    {f"Here is an example of tasks for reference: {json.dumps(example_tasks, indent=2)}" if example_tasks else ""}

    Return your response as a valid JSON array with each task as a separate object. The JSON structure should look like this:
    tasks = [
      {{
        "taskId": "T-YYYY-MM-W##-##",
        "title": "Action-oriented task title",
        "priority": "High/Medium/Low",
        "dueDate": "YYYY-MM-DD",
        "status": "Not Started",
        "context": "Detailed context about the farm conditions relevant to this task",
        "taskDescription": "A very Detailed and Comprehensive explanation of what the task involves and why it's important. It should be a complete paragraph",
        "steps": [
          "Detailed instruction", #Step:1
          "Detailed instruction", # Step:2
          "..."
        ],
        "supportingInformation": "Additional information about the importance and benefits of completing this task",
        "followUp": "Actions to take after task completion",
        "dependencies": [
          "Dependency 1: Description of what this task depends on",
          "Dependency 2: Another dependency",
          "..."
        ],


      }},
      {{ ... }}
    ]

    Make sure all tasks are relevant to the current farm conditions, growth stage, weather forecast. Use local terminology from {parameters.get('farmLocation', '')} where appropriate that would help farmers.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": task_prompt}],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=1,  
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content



if __name__ == "__main__":
    parameters = {
        "cropName": "Wheat",
        "farmLocation": "Rawalpindi, Punjab, Pakistan",
        "soilType": "Clay",
        "waterSource": "Groundwater",
        "growthStage": "Vegetative",
        "growingConditions": "Dry",
        "moistureLevel": "Low",
        "irrigationType": "Drip",
        "waterAvailability": "Limited",
        "fertilizerType": "NPK",
        "weatherForecast": """
          2025-04-23
          Condition: Sunny
          Max Temp: 35.0°C
          Min Temp: 20.6°C (69.1°F)
          Avg Temp: 27.8°C (82.0°F)
          Humidity: 14%
          Precipitation: 0.0 mm
          Wind: 18.7 kph

          2025-04-24
          Condition: Sunny
          Max Temp: 36.3°C
          Min Temp: 21.6°C (70.9°F)
          Avg Temp: 28.6°C (83.5°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 19.8 kph

          2025-04-25
          Condition: Sunny
          Max Temp: 37.4°C
          Min Temp: 20.9°C (69.6°F)
          Avg Temp: 29.1°C (84.3°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 16.9 kph

          2025-04-26
          Condition: Sunny
          Max Temp: 38.0°C
          Min Temp: 22.6°C (72.7°F)
          Avg Temp: 29.7°C (85.4°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 15.1 kph

          2025-04-27
          Condition: Sunny
          Max Temp: 38.8°C
          Min Temp: 21.4°C (70.5°F)
          Avg Temp: 30.3°C (86.5°F)
          Humidity: 16%
          Precipitation: 0.0 mm
          Wind: 14.4 kph

          2025-04-28
          Condition: Sunny
          Max Temp: 39.3°C
          Min Temp: 23.0°C (73.4°F)
          Avg Temp: 29.6°C (85.3°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 17.3 kph

          2025-04-29
          Condition: Sunny
          Max Temp: 40.2°C
          Min Temp: 24.5°C (76.1°F)
          Avg Temp: 32.8°C (91.0°F)
          Humidity: 11%
          Precipitation: 0.0 mm
          Wind: 13.0 kph""",
    }

    farm_report = """The crop is currently in the tillering stage, approximately 30 days after sowing on 2025-2-16, and appears healthy with a vibrant green color. The growth stage assessment indicates that the crop is developing as expected for this period. The soil condition seems moist and fertile, with a mix of clay and loamy texture, suitable for wheat cultivation. No visible signs of pests or diseases are observed on the crop. Weed pressure seems minimal, with no significant presence of weeds competing with the crop. The drip irrigation method appears efficient, with no signs of over or under irrigation. No obvious nutrient deficiency indicators are visible on the crop. Overall, the crop health status is good, with the potential for a successful harvest."""

    previous_tasks = [
        {
            "taskId": "T-2025-04-W16-01",
            "title": "Irrigation System Maintenance",
            "priority": "Medium",
            "dueDate": "2025-04-19",
            "status": "Not Started",
        },
        {
            "taskId": "T-2025-04-W16-02",
            "title": "Apply Second NPK Fertilizer",
            "priority": "High",
            "dueDate": "2025-04-20",
            "status": "In Progress",
        },
    ]
    
    example_tasks = [
        {
            "taskId": "T-2025-04-W17-01",
            "title": "Optimize Irrigation Schedule for Hot Weather",
            "priority": "High",
            "dueDate": "2025-04-24",
            "status": "Not Started",
            "context": "With forecasted temperatures reaching 35-40°C and humidity at 14-16%, the wheat crop in tillering stage is at risk of moisture stress. Current moisture level is Low with limited water availability from groundwater source using drip irrigation.",
            "taskDescription": "Adjust the irrigation schedule to provide adequate moisture during the critical tillering stage while conserving limited water resources. Proper irrigation management during this period is essential for tiller development and will directly impact final yield. The current dry conditions combined with rising temperatures create a high risk of water stress that could permanently reduce the crop's yield potential.",
            "steps": [
                "Inspect the existing drip irrigation system for any clogs or damage",
                "Increase irrigation frequency from once per day to twice daily (early morning and evening)",
                " Reduce each irrigation session duration by 15% to conserve water while maintaining soil moisture",
                "Focus additional water on areas that show signs of stress (wilting or yellowing)",
                "Monitor soil moisture daily by checking 4-6 inches below surface",
            ],
            "supportingInformation": "Research shows that wheat yield can decrease by up to 50% when moisture stress occurs during the tillering stage. Optimizing irrigation during this period is critical for developing a strong root system and healthy tillers that will support grain development. The current tillering stage represents a critical period where water management directly impacts final yield potential.",
            "followUp": "Check soil moisture levels daily and observe plant vigor. Adjust irrigation schedule if conditions change or if plants show signs of continued stress despite irrigation adjustments.",
            "dependencies": [
                "Requires completion of Task T-2025-04-W16-01 (Irrigation System Maintenance)",
                "Requires stable electricity supply for pump operation",
            ],
        }
    ]


    tasks = generate_farm_tasks(parameters, farm_report, example_tasks)
    print(tasks)
