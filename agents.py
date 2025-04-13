from praisonaiagents import Agent, MCP
import ollama
import re
import multiprocessing
from dotenv import load_dotenv
import os
load_dotenv()  # Load variables from .env file

LLM_MODEL="ollama/llama3.2:1b"

def initialize_airbnb_agent():
    return Agent(
        instructions="""You are a travel planning assistant that specializes in finding Airbnb listings and retrieving detailed information about specific properties. 
        Your goal is to help users effortlessly plan their trips by providing relevant and structured data—without requiring an API key.

        You can:
        - Use **airbnb_search** to find Airbnb listings based on filters like location, price range, and number of guests. Always include direct links to the listings.
        - Use **airbnb_listing_details** to get comprehensive details about a specific property, including pricing, amenities, reviews, and availability. Always include direct links to the listings.

        Use the tools wisely to assist users in making informed travel decisions while respecting Airbnb’s guidelines.
        """,
        llm=LLM_MODEL,
        tools=MCP("npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt")
    )

def initialize_youtube_transcript_agent():
    return Agent(
        instructions="""
        You are an intelligent assistant specialized in extracting and analyzing transcripts from YouTube videos to help users gain insights or repurpose video content.
        Your goal is to help users effortlessly and structured data—without requiring an API key.

        You MUST:
        - Use **get_transcripts** to retrieve accurate transcripts and subtitles from YouTube videos.
        Use the tools wisely to assist users. Based on the provided results, use Function tool call returns. 
        """,
        llm=LLM_MODEL,
        tools=MCP("npx -y @sinco-lab/mcp-youtube-transcript")
    )


def initialize_google_serper_agent():
    serper_api_key = os.getenv("SERPER_API_KEY")
    return Agent(
        instructions="""You are a research and content extraction assistant designed to help users find, analyze, and summarize information from the web using the Serper API.
        You MUST:
        - Use **google_search** to perform web searches when the user is asking for general information, how-to guides, comparisons, news, or any content that could be sourced from the internet. This tool retrieves:
            - Perform web searches using user queries to find organic results, FAQs, related searches, and knowledge graph entries.
            - Handle a wide range of search intents: informational, comparative, educational, technical, current events, etc.
            - Always return useful summaries along with links to the most relevant pages.
          **Tool Parameters**
            - `q`: Required. The search query string (e.g., "how Kubernetes works", "latest AI trends 2025"). Retrieve from the prompt.
            - `gl`: Required. Geographic region code in ISO 3166-1 alpha-2 format (e.g., "us", "de", "gb"). Use "en".
            - `hl`: Required. Language code in ISO 639-1 format (e.g., "en", "fr", "es"). Use "en.
            - `location`: Required. Location for search results (e.g., 'SoHo, New York, United States', 'California, United States'). Use "United States".
          Always summarize the top results clearly and include direct URLs for reference.
        - Use **scrape** to extract content from a specific webpage when:
            - The user provides a URL and asks for content, summaries, or metadata
            - A relevant link was previously found via **google_search** and needs to be explored further
        Use the tools wisely to assist users. Based on the provided results, use Function tool call returns, retrieve only content.  
        Parse the JSON response carefully and extract **relevant fields**. Give the search results with TITLE, LINK, CONTENT or SNIPPET.
        """,
        llm=LLM_MODEL,
        tools=MCP("npx -y serper-search-scrape-mcp-server", env={"SERPER_API_KEY": serper_api_key})
    )

def initialize_tavily_agent():
    print("tavily agent")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    return Agent(
        instructions="""You are a real-time web research and content analysis assistant, leveraging Tavily's advanced search and extraction capabilities to deliver accurate and actionable information.
        You MUST:
        - **Use `tavily-search`** when:
        - Users ask for recent news, events, trends, or up-to-date information.
        - Broad information gathering is required, especially with preferences like content type, domains, or number of results.
        - You need to analyze multiple sources or present an overview of a topic.
        Always return a concise summary of the top results, including titles, short descriptions, and direct links.
        - **Use `tavily-extract`** when:
        - Users provide a specific URL and want key information, summaries, or insights from that page.
        - A relevant link is found via `tavily-search` and needs deeper inspection or extraction.
        Return the main content in a clean, readable format. Include metadata or structure when useful for the task (e.g., for research, documentation, or structured data collection).
        Use these tools wisely to assist users in making informed decisions based on real-time, trustworthy information from the web.
        Parse the JSON response carefully and extract relevant fields. Give the search results with TITLE, LINK, CONTENT.
        """,
        llm=LLM_MODEL,
        tools=MCP("npx -y tavily-mcp@0.1.4", env={"TAVILY_API_KEY": tavily_api_key})
    )

# to run the agent in a separate process
def agent_worker(agent_initializer, query, queue):
    try:
        agent = agent_initializer()
        result = agent.start(query)
        queue.put(result)
    except Exception as e:
        queue.put(f"Error: {e}")

# to call an agent in a separate process
def run_agent_in_process(agent_initializer, query: str) -> str:
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=agent_worker, args=(agent_initializer, query, queue))
    p.start()
    p.join()  # wait for the process to finish.
    return queue.get()

# to select an appropriate agent based on keyword detection.
def route_query(query: str) -> str:
    keywords = {
        "airbnb": initialize_airbnb_agent,
        "google": initialize_google_serper_agent,
        "tavily": initialize_tavily_agent,
        "youtube": initialize_youtube_transcript_agent,
        "serper": initialize_google_serper_agent,
        "search": lambda: "search_agent",
        "get": lambda: "search_agent",
        "list": lambda: "search_agent"
    }

    for key, agent_initializer in keywords.items():
        if re.search(rf"\b{key}\b", query, re.IGNORECASE):
            if key in ["airbnb", "google", "youtube", "tavily", "serper"]:
                return run_agent_in_process(agent_initializer, query)
            else:
                return ollama.generate(model=LLM_MODEL, prompt=query)["response"]

    return ollama.generate(model=LLM_MODEL, prompt=query)["response"]
