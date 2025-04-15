import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up API key from environment variable
openai.api_key = os.getenv("OpenAI_API_KEY")

def test_openai_connection():
    """Test the OpenAI API connection using the API key from .env file"""
    try:
        # Create a simple completion to test the API key
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate a brief AI use case for healthcare."}
            ]
        )
        
        # Print the response
        print("\nAPI Connection Successful!\n")
        print("Generated AI Use Case:")
        print(response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"\nError connecting to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    print(f"Using API Key: {os.getenv('OpenAI_API_KEY')[:10]}...")
    test_openai_connection()