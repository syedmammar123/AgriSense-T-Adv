import os
import json
from groq import Groq
from datetime import datetime

EXAMPLE_ADVISORY = {
  "id": "A-2025-04-W17",
  "title": "Weekly Farm Advisory",
  "dateRange": "April 23-29, 2025",
  "cropStatus": "Wheat at tillering stage (30 days after sowing)",
  "healthStatus": "Good, vibrant green color",
  "weatherAlert": "Rising temperatures (reaching 40°C) with very low humidity",
  "priorityActions": "Optimize irrigation, apply NPK fertilizer, monitor heat stress",
  "riskLevel": "high", ## high, medium, low
  
  "cropDevelopment": {
    "title": "Crop Development Insights",
    "content": "Your wheat crop is currently in the tillering stage, a critical phase when the plant develops multiple stems that will eventually produce grain. At 30 days after sowing, your crop is progressing as expected with healthy green foliage. This stage will significantly impact your final yield potential.",
    "underground": "The root system is actively expanding, and the plants are establishing their yield foundation. The next 2-3 weeks represent a critical window for tiller development."
  },
  
  "weatherImpact": {
    "title": "Weather Impact Analysis",
    "content": "The forecast shows consistently hot and dry conditions with temperatures climbing steadily to reach 40.2°C by April 29.",
    "risks": [
      {
        "name": "Heat Stress Risk",
        "level": "high",
        "description": "Temperatures above 35°C can reduce wheat photosynthesis efficiency and damage developing tillers"
      },
      {
        "name": "Moisture Loss Risk",
        "level": "high",
        "description": "Low humidity (11-16%) combined with high temperatures will accelerate soil moisture evaporation"
      },
      {
        "name": "Irrigation Demand",
        "level": "medium",
        "description": "Will increase by approximately 20-25% compared to normal requirements"
      }
    ],
    "recommendation": "Implement twice-daily irrigation cycles (early morning and evening) to maintain soil moisture during this heat wave."
  },
  
  "nutritionalRequirements": {
    "title": "Nutritional Requirements",
    "content": "Your wheat is entering a period of high nutrient demand as tillers develop. The second NPK application is now critical and should be prioritized by April 25th.",
    "nutrients": [
      {
        "name": "Nitrogen (N)",
        "benefit": "Supports vigorous tiller development and leaf growth"
      },
      {
        "name": "Phosphorus (P)",
        "benefit": "Promotes strong root development"
      },
      {
        "name": "Potassium (K)",
        "benefit": "Helps with water regulation and heat stress tolerance"
      }
    ],
    "recommendation": "Complete your NPK application before temperatures reach their peak, ideally during early morning hours when humidity is relatively higher."
  },
  
  "pestDiseaseWatch": {
    "title": "Pest & Disease Watch",
    "risks": [
      {
        "name": "Aphids",
        "level": "medium-high",
        "description": "Rising temperatures favor rapid reproduction"
      },
      {
        "name": "Leaf Rust",
        "level": "medium",
        "description": "Dry conditions may limit spread"
      },
      {
        "name": "Powdery Mildew",
        "level": "low",
        "description": "Requires higher humidity"
      }
    ],
    "warning": "Be especially vigilant for aphids, which thrive in hot conditions and can vector viruses. Check undersides of leaves every 2-3 days."
  },
  
  "waterManagement": {
    "title": "Water Management Strategy",
    "steps": [
      "Increase irrigation frequency to twice daily (5am and 7pm)",
      "Check moisture level at 4-6 inches below surface daily",
      "Inspect drip lines for clogging due to mineral build-up in these hot conditions",
      "Consider temporary shade structures for most vulnerable sections if temperatures exceed 38°C for extended periods"
    ]
  },
  
  "lookingAhead": {
    "title": "Looking Ahead: Next Two Weeks",
    "predictions": [
      "Your crop will be transitioning from tillering to stem elongation stage",
      "Heat stress may accelerate development, potentially shortening growing season",
      "Prepare for foliar nutrient spray containing micronutrients in 7-10 days",
      "Heat-protective agents may be needed if hot conditions persist"
    ]
  },
  
  "resourcePlanning": {
    "title": "Resource Planning",
    "secureNow": [
      "Additional drip irrigation maintenance supplies",
      "Foliar spray containing zinc and manganese",
      "Heat-stress mitigating products"
    ],
    "scheduleSoon": [
      "Irrigation system thorough inspection",
      "Follow-up tissue analysis to confirm nutrient status"
    ]
  }
};

EXAMPLE_TASKS  =[
    {
      "taskId": "T-2025-04-W17-01",
      "title": "Optimize Irrigation Schedule for Hot Weather",
      "priority": "High",
      "dueDate": "2025-04-24 to 2025-04-26",
      "status": "Not Started",
      "context": "With forecasted temperatures reaching 35-40\u00b0C and humidity at 14-16%, the wheat crop in tillering stage is at risk of moisture stress. Current moisture level is Low with limited water availability from groundwater source using drip irrigation.",
      "taskDescription": "Adjust the irrigation schedule to provide adequate moisture during the critical tillering stage while conserving limited water resources. Proper irrigation management during this period is essential for tiller development and will directly impact final yield. The current dry conditions combined with rising temperatures create a high risk of water stress that could permanently reduce the crop's yield potential.",
      "steps": [
        "Step 1: Inspect the existing drip irrigation system for any clogs or damage",
        "Step 2: Increase irrigation frequency from once per day to twice daily (early morning and evening)",
        "Step 3: Reduce each irrigation session duration by 15% to conserve water while maintaining soil moisture",
        "Step 4: Focus additional water on areas that show signs of stress (wilting or yellowing)",
        "Step 5: Monitor soil moisture daily by checking 4-6 inches below surface"
      ],
      "supportingInformation": "Research shows that wheat yield can decrease by up to 50% when moisture stress occurs during the tillering stage. Optimizing irrigation during this period is critical for developing a strong root system and healthy tillers that will support grain development. The current tillering stage represents a critical period where water management directly impacts final yield potential.",
      "followUp": "Check soil moisture levels daily and observe plant vigor. Adjust irrigation schedule if conditions change or if plants show signs of continued stress despite irrigation adjustments.",
      "dependencies": [
        "Requires completion of Task T-2025-04-W16-01 (Irrigation System Maintenance)",
        "Requires stable electricity supply for pump operation"
      ]
    },
    {
      "taskId": "T-2025-04-W17-02",
      "title": "Apply Second NPK Fertilizer Application",
      "priority": "High",
      "dueDate": "2025-04-25",
      "status": "Not Started",
      "context": "The crop is currently in the tillering stage and requires a second application of NPK fertilizer to support healthy growth and development. The current soil condition seems moist and fertile, but the crop's nutritional needs are increasing.",
      "taskDescription": "Apply the second dose of NPK fertilizer to provide essential nutrients for wheat growth during the tillering and stem elongation stages. This application will help promote healthy tiller development, enhance root growth, and increase the crop's resistance to diseases and pests. The second NPK application is crucial for maximizing yield potential and improving grain quality.",
      "steps": [
        "Step 1: Prepare the required amount of NPK fertilizer according to the recommended dose",
        "Step 2: Ensure the fertilizer is evenly spread across the field using a suitable spreading method",
        "Step 3: Incorporate the fertilizer into the soil through light irrigation or mechanical mixing",
        "Step 4: Monitor the crop's response to the fertilizer application and adjust future applications as needed"
      ],
      "supportingInformation": "Split nitrogen applications are recommended during the tillering and stem elongation stages to optimize wheat yields. The second NPK application will provide essential nutrients for continued healthy growth and development.",
      "followUp": "Monitor the crop's response to the fertilizer application and adjust future applications as needed. Keep records of fertilizer applications for future reference.",
      "dependencies": [
        "Requires completion of Task T-2025-04-W16-02 (Apply Second NPK Fertilizer) or confirmation that it was completed successfully",
        "Requires suitable weather conditions (not too hot or windy)"
      ]
    },
    {
      "taskId": "T-2025-04-W17-03",
      "title": "Monitor for Foliar Diseases and Pests",
      "priority": "Medium",
      "dueDate": "2025-04-24 to 2025-04-29",
      "status": "Not Started",
      "context": "As the wheat crop develops, it becomes more susceptible to foliar diseases and pests. The current weather forecast indicates sunny conditions with rising temperatures, which can exacerbate disease development.",
      "taskDescription": "Regularly inspect the crop for signs of foliar diseases (e.g., yellow rust, powdery mildew) and pests (e.g., aphids, stem borers). Early detection is crucial for effective management and minimizing yield losses. Monitor the crop at least twice a week, focusing on areas with poor air circulation or previous disease/pest issues.",
      "steps": [
        "Step 1: Conduct a thorough visual inspection of the crop, looking for signs of disease or pest infestation",
        "Step 2: Use a magnifying glass or hand lens to examine suspicious symptoms more closely",
        "Step 3: Record observations and note any changes over time",
        "Step 4: Consult with local agricultural experts or extension services if unsure about disease/pest identification or management"
      ],
      "supportingInformation": "Foliar diseases and pests can significantly impact wheat yields if left unchecked. Regular monitoring allows for early intervention, reducing the risk of yield losses and ensuring a healthier crop.",
      "followUp": "Continue monitoring the crop regularly and implement control measures if necessary. Keep records of observations and actions taken.",
      "dependencies": [
        "Requires clear weather conditions for effective monitoring"
      ]
    },
    {
      "taskId": "T-2025-04-W17-04",
      "title": "Weed Control and Soil Moisture Management",
      "priority": "Medium",
      "dueDate": "2025-04-27 to 2025-04-29",
      "status": "Not Started",
      "context": "Weed pressure seems minimal, but continued management is essential to prevent competition for water and nutrients. The current soil moisture level is low, and conservation is crucial.",
      "taskDescription": "Control weeds through manual removal or suitable herbicides to prevent competition for water and nutrients. Additionally, maintain soil moisture through careful irrigation management, ensuring the soil remains moist but not waterlogged.",
      "steps": [
        "Step 1: Inspect the field for weeds and remove them manually or with herbicides",
        "Step 2: Adjust irrigation schedules to conserve soil moisture",
        "Step 3: Monitor soil moisture levels regularly",
        "Step 4: Consider using mulch or other soil conservation techniques"
      ],
      "supportingInformation": "Weed control and soil moisture management are critical for optimizing wheat growth and yield. Effective weed control reduces competition for resources, while proper soil moisture management ensures healthy root development.",
      "followUp": "Regularly inspect the field for new weed growth and adjust irrigation schedules as needed. Continue monitoring soil moisture levels.",
      "dependencies": [
        "Requires suitable weather conditions (not too hot or windy) for herbicide application",
        "Requires access to necessary herbicides and equipment"
      ]
    },
    {
      "taskId": "T-2025-04-W17-05",
      "title": "Irrigation System Maintenance and Repair",
      "priority": "Low",
      "dueDate": "2025-04-24 to 2025-04-29",
      "status": "Not Started",
      "context": "The drip irrigation system appears efficient, but regular maintenance is essential to ensure continued optimal performance.",
      "taskDescription": "Perform routine maintenance on the drip irrigation system to ensure it remains in good working condition. Check for clogs, damage, or leaks, and make repairs as needed.",
      "steps": [
        "Inspect the irrigation system for any damage or leaks",
        " Clean or replace clogged emitters or filters",
        " Check for proper water pressure and adjust as needed",
        " Record maintenance activities for future reference"
      ],
      "supportingInformation": "Regular maintenance of the irrigation system ensures efficient water use and reduces the risk of water-borne diseases. A well-maintained system also helps to prevent water stress and promotes healthy crop growth.",
      "followUp": "Schedule regular maintenance checks to ensure the irrigation system continues to function optimally.",
      "dependencies": [
        "Requires access to necessary tools and spare parts"
      ]
    }
  ]

def generate_weekly_advisory(
    parameters,
    farm_report,
    farm_tasks_for_upcoming_week=EXAMPLE_TASKS,
    example_advisory=EXAMPLE_ADVISORY,
    weather_data = None
):
    """
    Generate weekly farm advisory based on farm report, parameters, and upcoming tasks
    with structured output matching the desired format.

    Args:
        parameters: Dictionary containing farm parameters (crop, location, soil type, etc.)
        farm_report: String containing the latest farm condition report
        farm_tasks_for_upcoming_week: List of dictionaries containing upcoming tasks (optional)
        example_advisory: Example advisory to guide the LLM (optional)

    Returns:
        JSON formatted advisory matching the exact desired structure
    """

    # Create advisory generation prompt with all available information
    advisory_prompt = f"""
    I need to generate a comprehensive weekly farm advisory for a {parameters.get('crop', '')} farm in {parameters.get('farmLocation', '')}.
    The advisory must follow EXACTLY the structure and format provided in the example. Do not deviate from this structure.

    ## FARM REPORT (Generated on {datetime.now().strftime('%Y-%m-%d')}):
    {farm_report}

    ## FARM PARAMETERS:
    - Crop: {parameters.get('crop', '')}
    - Location: {parameters.get('farmLocation', '')}
    - Growth Stage: {parameters.get('currentGrowthStage', '')}
    - Soil Type: {parameters.get('soilType', '')}
    - Sowing Date: {parameters.get('sowingDate', '')}
    - Water Source: {parameters.get('waterSource', '')}
    - Irrigation Type: {parameters.get('irrigationType', '')}
    - Water Availability: {parameters.get('waterAvailabilityStatus', '')}
    - Fertilizer Type: {parameters.get('fertilizersUsed', '')}


    ## WEATHER FORECAST (Next 7 days):
    {weather_data}

    ## UPCOMING WEEK'S TASKS:
    {json.dumps(farm_tasks_for_upcoming_week, indent=2) if farm_tasks_for_upcoming_week else "No tasks avaliable for upcoming week."}

    {f"Here is an example of tasks for reference: {json.dumps(example_advisory, indent=2)}" if example_advisory else ""}

    Generate the weekly advisory.
    Return your response as a valid JSON object. The JSON structure should look exactly like this:

    advisory = {{
      "id": "A-YYYY-MM-WWW",  ## Week number
      "title": "Weekly Farm Advisory",
      "dateRange": "Month Day-Day, Year",
      "cropStatus": "Crop at growth stage (days after sowing)",
      "healthStatus": "Health assessment",
      "weatherAlert": "Key weather concern",
      "priorityActions": "Top 3 priority actions",
      "riskLevel": "high/medium/low",

      "cropDevelopment": {{
        "title": "Crop Development Insights",
        "content": "Detailed content",
        "underground": "Root development info"
      }},

      "weatherImpact": {{
        "title": "Weather Impact Analysis",
        "content": "Weather summary",
        "risks": [
          {{
            "name": "Risk name",
            "level": "high/medium/low",
            "description": "Risk description"
          }}
        ],
        "recommendation": "Specific recommendation"
      }},

      "nutritionalRequirements": {{
        "title": "Nutritional Requirements",
        "content": "Nutrition summary",
        "nutrients": [
          {{
            "name": "Nutrient name",
            "benefit": "Nutrient benefit"
          }}
        ],
        "recommendation": "Specific recommendation"
      }},

      "pestDiseaseWatch": {{
        "title": "Pest & Disease Watch",
        "risks": [
          {{
            "name": "Pest/disease name",
            "level": "high/medium/low",
            "description": "Description"
          }}
        ],
        "warning": "General warning"
      }},

      "waterManagement": {{
        "title": "Water Management Strategy",
        "steps": [
          "Step 1",
          "Step 2"
        ]
      }},

      "lookingAhead": {{
        "title": "Looking Ahead: Next Two Weeks",
        "predictions": [
          "Prediction 1",
          "Prediction 2"
        ]
      }},

      "resourcePlanning": {{
        "title": "Resource Planning",
        "secureNow": [
          "Item 1",
          "Item 2"
        ],
        "scheduleSoon": [
          "Action 1",
          "Action 2"
        ]
      }}
    }}

    Make sure to:
    1. Use the exact same field names and structure
    2. Include all sections exactly as shown
    3. Maintain the same JSON formatting
    4. Use real data from the provided parameters and farm report
    5. Focus on actionable recommendations specific to the current conditions

    Return ONLY the JSON output with no additional text or explanation.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": advisory_prompt}],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    # Parse and return the response
    try:
        advisory_json = json.loads(response.choices[0].message.content)
        return advisory_json
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse advisory response",
            "details": str(e),
            "raw_response": response.choices[0].message.content,
        }



if __name__ == "__main__":
    import json

    # Sample parameters
    parameters = {
        "crop": "Wheat",
        "farmLocation": "Rawalpindi, Punjab, Pakistan",
        "soilType": "Clay",
        "waterSource": "Groundwater",
        "currentGrowthStage": "Vegetative",
        "irrigationType": "Drip",
        "waterAvailability": "Limited",
        "fertilizerType": "NPK",
        "currentWeather": """
          2025-05-2
          Condition: Sunny
          Max Temp: 35.0°C
          Min Temp: 20.6°C (69.1°F)
          Avg Temp: 27.8°C (82.0°F)
          Humidity: 14%
          Precipitation: 0.0 mm
          Wind: 18.7 kph

          2025-05-3
          Condition: Sunny
          Max Temp: 36.3°C
          Min Temp: 21.6°C (70.9°F)
          Avg Temp: 28.6°C (83.5°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 19.8 kph

          2025-5-4
          Condition: Sunny
          Max Temp: 37.4°C
          Min Temp: 20.9°C (69.6°F)
          Avg Temp: 29.1°C (84.3°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 16.9 kph

          2025-05-6
          Condition: Sunny
          Max Temp: 38.0°C
          Min Temp: 22.6°C (72.7°F)
          Avg Temp: 29.7°C (85.4°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 15.1 kph

          2025-05-7
          Condition: Sunny
          Max Temp: 38.8°C
          Min Temp: 21.4°C (70.5°F)
          Avg Temp: 30.3°C (86.5°F)
          Humidity: 16%
          Precipitation: 0.0 mm
          Wind: 14.4 kph

          2025-05-8
          Condition: Sunny
          Max Temp: 39.3°C
          Min Temp: 23.0°C (73.4°F)
          Avg Temp: 29.6°C (85.3°F)
          Humidity: 15%
          Precipitation: 0.0 mm
          Wind: 17.3 kph

          2025-05-9
          Condition: Sunny
          Max Temp: 40.2°C
          Min Temp: 24.5°C (76.1°F)
          Avg Temp: 32.8°C (91.0°F)
          Humidity: 11%
          Precipitation: 0.0 mm
          Wind: 13.0 kph""",
    }

    # Sample farm report
    farm_report = """The crop is in the vegetative growth stage, with vibrant green color and healthy appearance. Growth stage assessment indicates uniform emergence and development. Soil condition evaluation shows clay soil with adequate moisture. No visible pests or diseases are present. Weed pressure is low. Irrigation efficiency appears optimal with drip irrigation. No nutrient deficiency indicators are visible."""

    # Sample upcoming tasks
    farm_tasks_for_upcoming_week = [
        {
            "taskId": "T-2025-04-W17-01",
            "title": "Optimize Irrigation Schedule for Hot Weather",
            "priority": "High",
            "dueDate": "2025-04-24 to 2025-04-26",
            "status": "Not Started",
            "context": "With forecasted temperatures reaching 35-40°C and humidity at 14-16%, the wheat crop in tillering stage is at risk of moisture stress.",
            "taskDescription": "Adjust the irrigation schedule to provide adequate moisture during the critical tillering stage while conserving limited water resources.",
            "steps": [
                "Step 1: Inspect the existing drip irrigation system for any clogs or damage",
                "Step 2: Increase irrigation frequency from once per day to twice daily (early morning and evening)",
                "Step 3: Reduce each irrigation session duration by 15% to conserve water while maintaining soil moisture",
                "Step 4: Focus additional water on areas that show signs of stress (wilting or yellowing)",
                "Step 5: Monitor soil moisture daily by checking 4-6 inches below surface",
            ],
        },
        {
            "taskId": "T-2025-04-W17-02",
            "title": "Apply Second NPK Fertilizer Application",
            "priority": "High",
            "dueDate": "2025-04-25",
            "status": "Not Started",
            "context": "The crop is currently in the tillering stage and requires a second application of NPK fertilizer to support healthy growth and development.",
            "taskDescription": "Apply the second dose of NPK fertilizer to provide essential nutrients for wheat growth during the tillering and stem elongation stages.",
            "steps": [
                "Prepare the required amount of NPK fertilizer according to the recommended dose",
                "Ensure the fertilizer is evenly spread across the field using a suitable spreading method",
                "Incorporate the fertilizer into the soil through light irrigation or mechanical mixing",
                "Monitor the crop's response to the fertilizer application",
            ],
        },
    ]

    # Generate advisory
    advisory = generate_weekly_advisory(
        parameters, farm_report
    )
    print(json.dumps(advisory, indent=2))
