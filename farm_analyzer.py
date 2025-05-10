import os
from typing import Dict, List, Union
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def generate_farm_report(
    image_urls: Union[str, List[str]], parameters: Dict[str, str]
) -> str:
    """
    Generate a detailed report about the farm based on the provided image URLs

    Args:
        image_urls: URL(s) to the image file(s)
        parameters: Dictionary containing farm parameters

    Returns:
        Detailed farm report
    """
    if isinstance(image_urls, str):
        image_urls = [image_urls]

    report_prompt = f"""
    I am providing you images from a {parameters.get('crop', '')} farm in {parameters.get('farmLocation', '')}.

    Additional context:
    - Growth stage: {parameters.get('currentGrowthStage', 'Not specified')}
    - Soil type: {parameters.get('soilType', 'Not specified')}
    - Current weather: {parameters.get('currentWeather', 'Not specified')}
    - Sowing date: {parameters.get('sowingDate', 'Not specified')}
    - Irrigation method: {parameters.get('irrigationType', 'Not specified')}

    Your job is to act as a professional crop inspector and provide a comprehensive farm assessment report covering:

    1. Current crop health status
    2. Growth stage assessment
    3. Soil condition evaluation
    4. Pest or disease identification (if any)
    5. Weed pressure assessment
    6. Irrigation efficiency
    7. Nutrient deficiency indicators (if any)


    Please provide specific, detailed information based on what you can observe in the images. Also, be confident on yourself. Say you speech as your are a professional crop inspector. Don't refer image to answer. Like just say refer it as crop.
    Don't add any sentence as 'However, without specific details, I cannot provide a comprehensive farm assessment report.' just be deterministic!

    In the last sentence just kinda summarize your finding. Remember I dont need any advises I just need report.

    I want a paragraph format
    Return your response in this json format:
    {{
    "report": "add entire report here",
    "summary": "oneline summary"
    }}
    """

    # Set up API client
    api_key = os.getenv("GROQ_API_KEY")
    # api_key = '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'
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    # Initialize Groq client with only the API key
    client = Groq(api_key=api_key)

    # Create message content with text and images
    message_content = [{"type": "text", "text": report_prompt}]
    
    for url in image_urls:
        message_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": url
                    },
            }
        )


    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": message_content}],
        response_format= { "type": "json_object" }
    )

    return response.choices[0].message.content
