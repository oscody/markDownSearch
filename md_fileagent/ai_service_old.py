import ollama
from pydantic import BaseModel
import json


# Define the structured output using Pydantic
class BlueInfo(BaseModel):
    color1: str
    color2: str
    color3: str

def OllamaService(prompt):
    model_name = "llama3.2"  # Specify your model version
    ollama_client = ollama.Client()

    # Prepare the messages with a prompt that encourages JSON output
    messages = [
        {"role": "system", "content": "You are a helpful Assistant."},
        {"role": "user", "content": f"{prompt} Return the answer as JSON."}
    ]

    # Call the model with the structured output format defined by BlueInfo
    response = ollama_client.chat(
        model=model_name,
        messages=messages,
        format=BlueInfo.model_json_schema(),  # Pass the schema for structured output
        options={
            "temperature": 0.2,
            "top_p": 0.5
        }
    )

    # Parse and validate the structured response using the Pydantic model
    blue_info = BlueInfo.model_validate_json(response['message']['content'])
    print(f"Structured Output:{blue_info}")

if __name__ == "__main__":
    OllamaService("give me 3 varitation of the color blue")


