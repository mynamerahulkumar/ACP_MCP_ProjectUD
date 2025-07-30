# Sequential Agent Health Insurer ACP

This project contains multiple implementations of health and insurance agents using different frameworks:

## Files

1. **smolagenthospital.py** - Original SmolAgent implementation
2. **langgraph_hospital_server.py** - LangGraph conversion of the SmolAgent
3. **crewAiInsurerservice.py** - CrewAI insurance service
4. **test_langgraph_client.py** - Client to test LangGraph agents

## LangGraph Implementation

The `langgraph_hospital_server.py` converts the SmolAgent functionality to use LangGraph with the following features:

### Agents
- **health_agent**: Handles general health questions using search and LLM
- **doctor_finder_agent**: Specialized agent for finding doctors by location and specialty

### Key Differences from SmolAgent
- Uses LangGraph for workflow orchestration
- Implements state management with TypedDict
- Uses LangChain tools and agents
- More structured approach to query processing

### Workflow Features
- **State Management**: Tracks messages, queries, and responses
- **Tool Integration**: Uses DuckDuckGo search for current information
- **Structured Processing**: Separates information extraction and search

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. Run the LangGraph server:
   ```bash
   python langgraph_hospital_server.py
   ```

4. Test with the client:
   ```bash
   python test_langgraph_client.py
   ```

## Architecture

```
Client (test_langgraph_client.py)
    ↓ HTTP (ACP SDK)
LangGraph Server (langgraph_hospital_server.py)
    ├── health_agent (LangGraph workflow)
    └── doctor_finder_agent (LangGraph workflow)
        ↓ Tools
    DuckDuckGo Search + OpenAI LLM
```

The LangGraph implementation provides more control over the agent workflow and better state management compared to the SmolAgent approach.