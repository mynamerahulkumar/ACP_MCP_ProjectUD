# ADK_ProjectUD
ADK with MCP project
# 1 CrewAI Insurance Agent
+-------------------+           HTTP (ACP SDK)           +-------------------+
|                   |  <------------------------------>  |                   |
|   acpclient.py    |                                   | crew_agent_server.py|
|  (Client Script)  |                                   |   (Agent Server)   |
|                   |                                   |                   |
| - Sends question  |                                   | - Receives question|
|   to agent        |                                   | - Uses CrewAI LLM  |
| - Prints answer   |                                   |   + RAG Tool       |
|                   |                                   |   + PDF Knowledge  |
+-------------------+                                   |   Base             |
                                                        | - Returns answer   |
                                                        +-------------------+
