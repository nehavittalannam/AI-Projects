import asyncio  # Import asyncio to use asyncio.run()
from typing import Any, Dict, List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.task import Console, HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import Swarm
from autogen_ext.models import AzureOpenAIChatCompletionClient
import requests
from autogen_ext.models import AzureOpenAIChatCompletionClient
import logging

logfilepath = "Llama_logs.log"
logging.basicConfig(filename=logfilepath, level=logging.INFO, format='%(asctime)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)

def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"

def refund_car(car_id: str) -> str:
    """Refund a car"""
    return f"car {car_id} refunded"

def generic_tool(user_query: str) -> str:
    try:
        # Formulate a prompt to the LLM to generate a response for a general query
        prompt = f"Answer the following general question:\n\n{user_query}\n\nResponse:"
        response = az_model_client.complete(prompt, max_tokens=200)  # Use the Azure LLM to generate the response
        generated_response = response['choices'][0]['text'].strip()
        return generated_response
    except Exception as e:
        print(f"Error generating response for generic query: {e}")
        return "Sorry, I couldn't generate a response at the moment."

az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="your_deployment_name",
    model="model_name",
    api_version="version",
    azure_endpoint="your_end_point",
    api_key= "your_api_key"
)
print(az_model_client)

travel_agent = AssistantAgent(
    "travel_agent",
    model_client=az_model_client,
    handoffs=["flights_refunder", "user","generic_agent","car_refunder"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    The car_refunder is in charge of refunding car rides.
    The generic agents does the general purose tasks.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=az_model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You only need flight reference numbers to refund a flight.
    You have the ability to refund a flight using the refund_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)

car_refunder = AssistantAgent(
    "car_refunder",
    model_client=az_model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_car],
    system_message="""You are an agent specialized in refunding car rides.
    You only need car reference numbers to refund a car rides.
    You have the ability to refund a car using the refund_car tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)

generic_agent = AssistantAgent(
    "generic_agent",
    model_client=az_model_client,
    handoffs=["manager_agent" , "user"],  # Always hand back to the Manager Agent after responding
    tools=[generic_tool],
    system_message="""You are the Generic Agent.
    Your role is to handle all queries and tasks that are not related to SQL operations. This includes:
    
    - Answering general inquiries and providing information on a variety of topics.
    - Assisting with tasks that require basic processing or handling outside of SQL operations.
    - Offering support for a wide range of requests that fall outside the scope of database management.
    
    When you respond to the user, you will hand off the task back to the Manager Agent for termination."""
)
termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, car_refunder,flights_refunder,generic_agent], termination_condition=termination)

task = "START"

# To keep track of communication history
communication_history = []

async def run_team_stream() -> None:
    start_time=time.time() #Start time of communication
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")
        # Record the communication
        communication_history.append(f"User: {user_message}")
        
        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]
        
        # Record the agent's response
        for msg in task_result.messages:
            if hasattr(msg, "content"):
                communication_history.append(f"{msg.source}: {msg.content}")
    
    # End time of the communication
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nDuration of communication: {duration:.2f} seconds")

    # Print communication history
    print("\n--- Communication History ---")
    for message in communication_history:
        print(message)
        
async def main():
    await run_team_stream()


if __name__ == "__main__":
    asyncio.run(main())
