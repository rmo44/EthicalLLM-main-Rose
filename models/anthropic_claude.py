import anthropic
from dotenv import load_dotenv
import os

def query_claude(prompt):
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    # Create a message
    message = client.messages.create(
        model="claude-3-opus-20240229",  
        max_tokens=1000,
        # We'll need to change this later 
        # temperature=0.7,
        # system="You are a ...",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    full_response = message.content[0].text 

        # Extracting the judgment score to store in the csv
    score = None
    for line in full_response.split('\n'):
        if line.startswith("Response judgment:"):
            score = line.split(':')[1].strip()
            break
    
    # Extracting  the justification from the response
    justification_parts = full_response.split('Justification:', 1)
    justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
    
    # Returning the actual response, score (integer part), and the justification part
    return full_response, score, justification