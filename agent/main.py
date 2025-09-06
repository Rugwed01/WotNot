import json
from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
from langchain_community.llms import Bedrock
from langchain.agents import initialize_agent, AgentType
from langchain_community.utilities.openapi import OpenAPISpec
from langchain_community.agent_toolkits.openapi.toolkit import RequestsToolkit
from langchain.prompts import ChatPromptTemplate
from . import oauth2  # Import the oauth2 module for endpoint security

# Load OpenAPI spec from file as raw text
with open("wotnot_openapi.json", "r") as f:
    openapi_raw = f.read()

# Use correct OpenAPISpec method
spec = OpenAPISpec.from_text(openapi_raw)
spec.base_url = "https://api.wotnot.io"

# Get tools
toolkit = RequestsToolkit(spec=spec)
tools = toolkit.get_tools()

# LLM
llm = Bedrock(
    model_id="anthropic.claude-v2",
    region_name="us-east-1",
    model_kwargs={"temperature": 0.2}
)

# Agent for existing functionality
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# FastAPI app
app = FastAPI()

# --- NEW FEATURE CODE STARTS HERE ---

# 1. Define the request model for the new feature using Pydantic
class MessageGenerationRequest(BaseModel):
    user_prompt: str

# 2. Create the new endpoint for message generation
@app.post("/generate-message/")
async def generate_message(
    request: MessageGenerationRequest,
    current_user: dict = Depends(oauth2.get_current_user) # Secure the endpoint
):
    """
    Receives a user prompt, generates a marketing message using the LLM,
    and returns the tweakable message.
    """
    
    # 3. Create a robust prompt template to guide the LLM
    # This template instructs the model to create a message AND include placeholders.
    template_string = """
    You are an expert marketing copywriter. Your task is to generate a message based on the user's request.
    The message you generate MUST include placeholders for any specific details that need to be personalized later, such as names, dates, or offers.
    Use the format {{placeholder_name}} for all placeholders. The placeholders should be logical and self-explanatory.

    Example Request: "A diwali wish for my customers"
    Example Output: "Hello {{customer_name}}, wishing you a bright and joyous Diwali! To celebrate, we're offering you {{offer_details}}."

    Now, please generate a message based on the following user request.

    User Request: {user_prompt}
    Generated Message:
    """
    
    prompt_template = ChatPromptTemplate.from_template(template_string)
    
    # 4. Create the chain to connect the prompt and the LLM
    chain = prompt_template | llm

    try:
        # 5. Invoke the chain with the user's prompt
        result = await chain.ainvoke({"user_prompt": request.user_prompt})
        
        # The result from a LangChain LLM is often the content string itself.
        # If it's an AIMessage object, you'd access it with result.content
        generated_text = result if isinstance(result, str) else result.content
        
        return {"generated_message": generated_text.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the message: {str(e)}")

# --- NEW FEATURE CODE ENDS HERE ---


# Existing endpoint for the agent
@app.post("/run-agent/")
async def run_agent(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "Find content for template, create it, and send to today's contacts.")
    try:
        # Note: agent.run is deprecated. Consider using agent.invoke for future compatibility.
        result = agent.run(prompt)
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}