import asyncio
from acp_sdk.client import Client
from colorama import Fore

async def test_health_agent():
    """Test the LangGraph health agent"""
    async with Client(base_url="http://localhost:8001") as hospital:
        # Test health-related query
        health_query = "What are the symptoms of diabetes and what treatments are available?"
        
        print(f"{Fore.CYAN}Testing Health Agent with query: {health_query}{Fore.RESET}")
        
        run1 = await hospital.run_sync(
            agent="health_agent", 
            input=health_query
        )
        
        content = run1.output[0].parts[0].content
        print(f"{Fore.GREEN}Health Agent Response:{Fore.RESET}")
        print(f"{Fore.LIGHTGREEN_EX}{content}{Fore.RESET}\n")

async def test_doctor_finder_agent():
    """Test the LangGraph doctor finder agent"""
    async with Client(base_url="http://localhost:8001") as hospital:
        # Test doctor finder query
        doctor_query = "I'm based in Atlanta, GA. Are there any cardiologists near me?"
        
        print(f"{Fore.CYAN}Testing Doctor Finder Agent with query: {doctor_query}{Fore.RESET}")
        
        run2 = await hospital.run_sync(
            agent="doctor_finder_agent", 
            input=doctor_query
        )
        
        content = run2.output[0].parts[0].content
        print(f"{Fore.BLUE}Doctor Finder Agent Response:{Fore.RESET}")
        print(f"{Fore.LIGHTBLUE_EX}{content}{Fore.RESET}\n")

async def main():
    """Run both agent tests"""
    print(f"{Fore.YELLOW}Testing LangGraph Hospital Server Agents{Fore.RESET}\n")
    
    await test_health_agent()
    await test_doctor_finder_agent()
    
    print(f"{Fore.YELLOW}All tests completed!{Fore.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
