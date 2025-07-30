from acp_sdk.client import Client
import asyncio
from colorama import Fore 

async def run_hospital_workflow() -> None:
    """
    Sequential workflow using LangGraph hospital agents and insurance agents
    """
    async with Client(base_url="http://localhost:8002") as langgraph_hospital, Client(base_url="http://localhost:8001") as insurer:
        # Step 1: Ask health question to LangGraph health agent
        print(f"{Fore.CYAN}Step 1: Consulting LangGraph Health Agent...{Fore.RESET}")
        
        run1 = await langgraph_hospital.run_sync(
            agent="health_agent", input="Do I need rehabilitation after a shoulder reconstruction?"
        )
        content = run1.output[0].parts[0].content
        print(f"{Fore.LIGHTMAGENTA_EX}Health Agent Response: {content}{Fore.RESET}\n")

        # Step 2: Use health context to ask insurance question
        print(f"{Fore.CYAN}Step 2: Consulting Insurance Policy Agent for Question: What is the waiting period for rehabilitation? {Fore.RESET}")
        
        run2 = await insurer.run_sync(
            agent="policy_agent", input=f"Context: {content}\n\nQuestion: What is the waiting period for rehabilitation?"
        )
        print(f"{Fore.YELLOW}Insurance Agent Response: {run2.output[0].parts[0].content}{Fore.RESET}\n")

async def run_doctor_finder_workflow() -> None:
    """
    Test the LangGraph doctor finder agent
    """
    async with Client(base_url="http://localhost:8002") as langgraph_hospital:
        print(f"{Fore.CYAN}Testing LangGraph Doctor Finder Agent...{Fore.RESET}")
        
        run1 = await langgraph_hospital.run_sync(
            agent="doctor_finder_agent", input="I'm based in Atlanta, GA. Are there any cardiologists near me?"
        )
        content = run1.output[0].parts[0].content
        print(f"{Fore.LIGHTBLUE_EX}Doctor Finder Response: {content}{Fore.RESET}\n")

async def main():
    """
    Run both workflows to demonstrate LangGraph agents
    """
    print(f"{Fore.GREEN}=== Sequential Agent Workflow with LangGraph ==={Fore.RESET}\n")
    
    try:
        # Run the sequential health + insurance workflow
        await run_hospital_workflow()
        
        print(f"{Fore.GREEN}--- Separator ---{Fore.RESET}\n")
        
        # Run the doctor finder workflow
        # await run_doctor_finder_workflow()
        
        print(f"{Fore.GREEN}=== All workflows completed successfully! ==={Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Error occurred: {str(e)}{Fore.RESET}")
        print(f"{Fore.RED}Make sure both servers are running:{Fore.RESET}")
        print(f"{Fore.RED}  - LangGraph Hospital Server: python langgraph_hospital_server.py (port 8001){Fore.RESET}")
        print(f"{Fore.RED}  - Insurance Server: python crewAIInsuranceAgentServer.py (port 8002){Fore.RESET}")
        
asyncio.run(main())