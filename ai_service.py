import ollama
from pydantic import BaseModel
from typing import Type



import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def OllamaService(prompt: str, schema: Type[BaseModel], model_name: str = "llama3.2"):
    ollama_client = ollama.Client()

    messages = [
        {"role": "system", "content": "You are a helpful Assistant."},
        {"role": "user", "content": f"{prompt} Return the answer as JSON."}
    ]

    response = ollama_client.chat(
        model=model_name,
        messages=messages,
        format=schema.model_json_schema(),  # Use the dynamic schema's JSON schema
        options={
            "temperature": 0.2,
            "top_p": 0.5
        }
    )

    structured_output = schema.model_validate_json(response['message']['content'])
    # print(f"Structured Output: {structured_output}")
    return structured_output


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def OpenAIService(prompt: str, schema: Type[BaseModel], model_name: str = "gpt-4o-2024-08-06"):
    mmessages = [
        {
            "role": "system", 
            "content": [{"type": "text", "data": "You are a helpful Assistant."}]
        },
        {
            "role": "user", 
            "content": [{"type": "text", "data": prompt}]
        }
    ]
    
    response = client.beta.chat.completions.parse(
        model=model_name,
        messages=mmessages,
        response_format=schema,
    )

    structured_result = response.choices[0].message.parsed
    print(structured_result)
    return structured_result
