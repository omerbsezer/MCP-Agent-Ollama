# MCP Ollama Agent

## Why this Repo?
- **No need MCP client tool** app, **No need using Remote LLM APIs** (OpenAI, Claude, Bedrock), Use **Local PC LLM models** instead of LLM APIs.
- MCP servers are normally connected to MCP Client tools (Claude, Cursor, Windsurf, VSCode). This repo doesn't have any MCP Client. 
- Instead of MCP client tool, this repo shows to connect MCP tools to Agent directly.
- Agent can automatically uses MCP tools, it speeds up automation and agent can use MCP tools independently.


## What is This Repo: MCP Ollama Agent?
- App runs GUI using Streamlit.
- To connect each MCP tools, agents are implemented for each tool. 
- PraisonAI library is used to run agent, MCP and Ollama together.
- According to the prompt, which agents will be used selected with key search. It might be better and smarter in the future.  
  - If the prompt includes "Google", "Serper", Google Serper agent will be called
  - If the prompt includes "Youtube", Youtube agent will be called 
  - If the prompt includes "Tavily", Tavily agent will be called
- To use Tavily and Serper, you must create .env file and add your APIs from Tavily and Serper.
  - https://tavily.com/ (each month 2000 request free, no credit card needed)
  - https://serper.dev/ (first 2500 request free, no credit card needed)
- It creates a generic helper that abstracts the process creation and call for any MCP-based agent. Then, simply map each keyword to its agent initializer and use that helper.


## Ollama
- To run LLM models on your local PC, you need to use Ollama.
  - Install: https://ollama.com/download
- It depends on your PC CPU/GPU Power, you can select to run which LLM model.
- If you have only CPU, you should use smaller models (e.g. Llama3.2:1b, Llama3.2:3b)
- If you have GPU, you should know the your GPU VRAM size. You can see the LLM model size on the Ollama page. 
  - Llama3.2:1b => 1.3GB
  - Llama3.2:3b => 2GB
  - Llama3.1:8b => 4.9GB
- While running the model on GPU, model size covers ~1.5x size on the VRAM. Llama3.1:8b is normally 4.9GB, but while running, it takes 6.9GB.    

## Run
- Install node, npm, npx on your PC. 
- python -m streamlit run app.py

## MCP & Examples
- MCP JSON response is important. If the response doesn't contain right information, agent will return that information.
- MCP Server is an adapter layer between the remote API and agent. If any change on the remote API, MCP server cannot give correct information.
- You can check whether MCP works correctly or not from Smithery (https://smithery.ai/)
  - For example, testing Airbnb MCP server using smithery: https://smithery.ai/server/@openbnb-org/mcp-server-airbnb/tools 

### Airbnb Sample Prompt
I want to book apartment using Airbnb. I will stay in Paris between 20.05.2025-30.05.2025, searching nightly min 40€ max 60€.

### Serper (Google) Sample Prompt
I want to search "how to learn LLM" on Google using Serper

### Tavily Sample Prompt
I want to search "how to learn LLM" using Tavily

### Youtube Sample Prompt
I want to search "how to learn LLM" using Tavily

## Demo



