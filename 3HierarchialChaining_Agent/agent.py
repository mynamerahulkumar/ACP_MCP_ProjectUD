import asyncio 
import nest_asyncio
from acp_sdk.client import Client
from smolagents import LiteLLMModel
from fastacp import AgentCollection, ACPCallingAgent
from colorama import Fore
nest_asyncio.apply()
from dotenv import load_dotenv
load_dotenv()
import os
os.environ['OPENAI_API_KEY']=os.getenv('OPENAI_API_KEY')
model = LiteLLMModel(
    model_id="openai/gpt-4"
)

async def run_hospital_workflow() -> None:
    try:
        async with Client(base_url="http://localhost:8001") as insurer, Client(base_url="http://localhost:8000") as hospital:
            print(f"{Fore.CYAN}Discovering agents...{Fore.RESET}")
            
            # agents discovery
            agent_collection = await AgentCollection.from_acp(insurer, hospital)  
            acp_agents = {agent.name: {'agent':agent, 'client':client} for client, agent in agent_collection.agents}
            
            print(f"{Fore.GREEN}Found agents: {list(acp_agents.keys())}{Fore.RESET}")
            
            # Let's try a simpler approach - directly call the agents instead of using ACPCallingAgent
            print(f"{Fore.CYAN}Calling health_agent directly...{Fore.RESET}")
            
            # Step 1: Call health agent
            health_response = await hospital.run_sync(
                agent="health_agent", 
                input="Do I need rehabilitation after a shoulder reconstruction?"
            )
            
            print(f"{Fore.CYAN}Debug - Health response structure: {health_response}{Fore.RESET}")
            
            # Handle different possible response structures
            if hasattr(health_response, 'output') and health_response.output:
                health_content = health_response.output[0].parts[0].content
            elif hasattr(health_response, 'messages') and health_response.messages:
                health_content = health_response.messages[0].parts[0].content  
            else:
                health_content = str(health_response)
                
            print(f"{Fore.LIGHTMAGENTA_EX}Health Agent Response: {health_content}{Fore.RESET}\n")
            
            # Step 2: Call insurance agent with context
            print(f"{Fore.CYAN}Calling policy_agent with context...{Fore.RESET}")
            insurance_query = f"Context: {health_content}\n\nQuestion: What is the waiting period for rehabilitation?"
            
            insurance_response = await insurer.run_sync(
                agent="policy_agent",
                input=insurance_query
            )
            
            print(f"{Fore.CYAN}Debug - Insurance response structure: {insurance_response}{Fore.RESET}")
            
            # Handle different possible response structures
            if hasattr(insurance_response, 'output') and insurance_response.output:
                insurance_content = insurance_response.output[0].parts[0].content
            elif hasattr(insurance_response, 'messages') and insurance_response.messages:
                insurance_content = insurance_response.messages[0].parts[0].content
            else:
                insurance_content = str(insurance_response)
                
            print(f"{Fore.YELLOW}Insurance Agent Response: {insurance_content}{Fore.RESET}\n")
            
            # Combine the results
            final_result = f"""
Based on the consultation:

Health Information: {health_content}

Insurance Information: {insurance_content}
"""
            print(f"{Fore.GREEN}Final Combined Result:{Fore.RESET}")
            print(f"{Fore.LIGHTGREEN_EX}{final_result}{Fore.RESET}")
            
    except Exception as e:
        print(f"{Fore.RED}Error occurred: {str(e)}{Fore.RESET}")
        print(f"{Fore.RED}Make sure both servers are running:{Fore.RESET}")
        print(f"{Fore.RED}- Insurance server on localhost:8001{Fore.RESET}")
        print(f"{Fore.RED}- Hospital server on localhost:8000{Fore.RESET}")
        import traceback
        traceback.print_exc()


asyncio.run(run_hospital_workflow())

        