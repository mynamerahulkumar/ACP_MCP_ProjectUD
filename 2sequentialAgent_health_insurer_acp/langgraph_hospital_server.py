from collections.abc import AsyncGenerator
from typing import TypedDict, Annotated
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server, Context
from dotenv import load_dotenv
import os

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

server = Server()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", max_tokens=2048, temperature=0)

# Define state for the graph
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    response: str

# Tools
search_tool = DuckDuckGoSearchRun()

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful health assistant for a hospital. 
    You help patients with health-related questions and provide information about hospital treatments.
    Use the search tool when you need current medical information or specific treatment details.
    Always provide accurate, helpful, and empathetic responses."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create agent
tools = [search_tool]
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Define nodes for the graph
def health_search_node(state: GraphState):
    """Node that processes health queries using search and LLM"""
    query = state["query"]
    
    # Run the agent with the query
    result = agent_executor.invoke({
        "input": query,
        "chat_history": []
    })
    
    response = result["output"]
    
    return {
        "messages": [HumanMessage(content=query), AIMessage(content=response)],
        "response": response
    }

def should_search(state: GraphState):
    """Determine if we need to search or can answer directly"""
    # For this simple example, we always search
    # In a more complex scenario, you could add logic here
    return "search"

# Build the graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("health_search", health_search_node)

# Set entry point
workflow.set_entry_point("health_search")

# Add edges
workflow.add_edge("health_search", END)

# Compile the graph
app = workflow.compile()

@server.agent()
async def health_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """LangGraph-based health agent that helps with hospital and health-related questions"""
    
    # Extract the user query
    prompt = input[0].parts[0].content
    
    # Create initial state
    initial_state = {
        "query": prompt,
        "messages": [],
        "response": ""
    }
    
    # Run the workflow
    final_state = app.invoke(initial_state)
    
    # Extract the response
    response = final_state["response"]
    
    yield Message(parts=[MessagePart(content=str(response))])

@server.agent()
async def doctor_finder_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """LangGraph-based doctor finder agent"""
    
    # Define a specialized state for doctor finding
    class DoctorState(TypedDict):
        messages: Annotated[list, add_messages]
        query: str
        location: str
        specialty: str
        response: str
    
    def extract_location_specialty(state: DoctorState):
        """Extract location and specialty from the query"""
        query = state["query"]
        
        # Use LLM to extract structured information
        extraction_prompt = f"""
        Extract the location and medical specialty from this query: "{query}"
        
        Return in format:
        Location: [extracted location or "not specified"]
        Specialty: [extracted specialty or "general practitioner"]
        """
        
        result = llm.invoke(extraction_prompt)
        
        # Simple parsing (in production, you'd want more robust parsing)
        lines = result.content.split('\n')
        location = "not specified"
        specialty = "general practitioner"
        
        for line in lines:
            if line.startswith("Location:"):
                location = line.replace("Location:", "").strip()
            elif line.startswith("Specialty:"):
                specialty = line.replace("Specialty:", "").strip()
        
        return {
            "location": location,
            "specialty": specialty
        }
    
    def search_doctors(state: DoctorState):
        """Search for doctors based on location and specialty"""
        location = state["location"]
        specialty = state["specialty"]
        
        search_query = f"find {specialty} doctors near {location} contact information"
        search_result = search_tool.run(search_query)
        
        # Create a comprehensive response
        response_prompt = f"""
        Based on this search result about {specialty} doctors near {location}:
        
        {search_result}
        
        Provide a helpful response that includes:
        1. Available doctors or clinics
        2. Contact information if available
        3. Suggestions for next steps
        
        Make the response conversational and helpful.
        """
        
        response = llm.invoke(response_prompt)
        
        return {
            "response": response.content,
            "messages": [
                HumanMessage(content=state["query"]),
                AIMessage(content=response.content)
            ]
        }
    
    # Build doctor finder workflow
    doctor_workflow = StateGraph(DoctorState)
    doctor_workflow.add_node("extract_info", extract_location_specialty)
    doctor_workflow.add_node("search_doctors", search_doctors)
    
    doctor_workflow.set_entry_point("extract_info")
    doctor_workflow.add_edge("extract_info", "search_doctors")
    doctor_workflow.add_edge("search_doctors", END)
    
    doctor_app = doctor_workflow.compile()
    
    # Extract the user query
    prompt = input[0].parts[0].content
    
    # Create initial state
    initial_state = {
        "query": prompt,
        "messages": [],
        "location": "",
        "specialty": "",
        "response": ""
    }
    
    # Run the workflow
    final_state = doctor_app.invoke(initial_state)
    
    # Extract the response
    response = final_state["response"]
    
    yield Message(parts=[MessagePart(content=str(response))])

if __name__ == "__main__":
    print("LangGraph Hospital Server running...")
    server.run(port=8002)
