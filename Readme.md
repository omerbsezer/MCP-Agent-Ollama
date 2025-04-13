# MCP Ollama Agent
- App runs with streamlit for GUI
- To connect each MCP tools, agents are implemented for each tool.
- According to the prompt, which agents will be used selected with key search.
  - If the prompt includes "Google", Google Serper agent will be called
  - If the prompt includes "Youtube", Youtube agent will be called 
- It creates a generic helper that abstracts the process creation and call for any MCP-based agent. Then, simply map each keyword to its agent initializer and use that helper.


## Run
- python -m streamlit run app.py

## Example



## Demo



