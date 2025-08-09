import asyncio 
import nest_asyncio
from acp_sdk.client import Client
from smolagents import LiteLLMModel
from fastacp import AgentCollection, ACPCallingAgent
from colorama import Fore
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
            print(f"{Fore.CYAN}🔍 Discovering agents...{Fore.RESET}")
            
            # agents discovery
            agent_collection = await AgentCollection.from_acp(insurer, hospital)  
            acp_agents = {agent.name: {'agent':agent, 'client':client} for client, agent in agent_collection.agents}
            
            print(f"{Fore.GREEN}✅ Found agents: {list(acp_agents.keys())}{Fore.RESET}")
            print(f"Agent details: {acp_agents}")
            
            # Skip FastACP orchestration due to compatibility issues with LiteLLM
            # Fallback to direct sequential agent calls which work reliably
            
            result = await run_direct_agent_calls(insurer, hospital)
            print(f"{Fore.YELLOW}✨ Direct Call Result: {result}{Fore.RESET}")
            
            # Uncomment below to try FastACP orchestration if issues are resolved
            # try:
            #     print(f"{Fore.CYAN}🤖 Attempting FastACP orchestration...{Fore.RESET}")
            #     
            #     # passing the agents as tools to ACPCallingAgent
            #     acpagent = ACPCallingAgent(acp_agents=acp_agents, model=model)
            #     print("acp agent created---")
            #     # running the agent with a user query
            #     result = await acpagent.run("do i need rehabilitation after a shoulder reconstruction and what is the waiting period from my insurance?")
            #     print(f"{Fore.YELLOW}✨ FastACP Result: {result}{Fore.RESET}")
            #     
            # except Exception as orchestration_error:
            #     print(f"{Fore.YELLOW}⚠️ FastACP orchestration failed: {str(orchestration_error)}{Fore.RESET}")
            #     print(f"{Fore.CYAN}🔄 Falling back to direct agent calls...{Fore.RESET}")
            #     
            #     # Fallback to direct sequential agent calls
            #     result = await run_direct_agent_calls(insurer, hospital)
            #     print(f"{Fore.YELLOW}✨ Direct Call Result: {result}{Fore.RESET}")
                
    except Exception as e:
        print(f"{Fore.RED}❌ Error in workflow: {str(e)}{Fore.RESET}")
        import traceback
        traceback.print_exc()

async def run_direct_agent_calls(insurer, hospital):
    """Fallback method using direct agent calls"""
    try:
        # Step 1: Get health information
        print(f"{Fore.CYAN}🏥 Step 1: Consulting health agent...{Fore.RESET}")
        
        health_query = "Do I need rehabilitation after a shoulder reconstruction? What does the rehabilitation process involve and how long does it typically take?"
        
        health_response = await hospital.run_sync(
            agent="health_agent",
            input=health_query
        )
        
        # Extract health content safely
        if hasattr(health_response, 'output') and health_response.output:
            health_content = health_response.output[0].parts[0].content
        elif hasattr(health_response, 'messages') and health_response.messages:
            health_content = health_response.messages[0].parts[0].content
        else:
            health_content = str(health_response)
        
        print(f"{Fore.GREEN}✅ Health consultation completed{Fore.RESET}")
        
        # Step 2: Get insurance information with health context
        print(f"{Fore.CYAN}🏛️ Step 2: Consulting insurance agent...{Fore.RESET}")
        
        insurance_query = f"""
        Context: {health_content}
        
        Based on the above medical information about shoulder reconstruction rehabilitation, 
        what is the waiting period for my insurance coverage? What are the coverage details?
        """
        
        insurance_response = await insurer.run_sync(
            agent="policy_agent",
            input=insurance_query
        )
        
        # Extract insurance content safely
        if hasattr(insurance_response, 'output') and insurance_response.output:
            insurance_content = insurance_response.output[0].parts[0].content
        elif hasattr(insurance_response, 'messages') and insurance_response.messages:
            insurance_content = insurance_response.messages[0].parts[0].content
        else:
            insurance_content = str(insurance_response)
        
        print(f"{Fore.GREEN}✅ Insurance consultation completed{Fore.RESET}")
        
        # Combine results
        combined_result = f"""
{Fore.LIGHTBLUE_EX}=== COMPREHENSIVE SHOULDER SURGERY CONSULTATION ==={Fore.RESET}

{Fore.LIGHTGREEN_EX}🏥 MEDICAL INFORMATION:{Fore.RESET}
{health_content}

{Fore.LIGHTCYAN_EX}🏛️ INSURANCE COVERAGE INFORMATION:{Fore.RESET}
{insurance_content}

{Fore.LIGHTYELLOW_EX}📋 INTEGRATED SUMMARY:{Fore.RESET}
This consultation provides both medical guidance on shoulder reconstruction rehabilitation 
and your specific insurance coverage details, giving you a complete picture for planning 
your recovery process.
"""
        
        return combined_result
        
    except Exception as e:
        return f"Error in direct agent calls: {str(e)}"


asyncio.run(run_hospital_workflow())

        