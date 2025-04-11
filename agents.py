from praisonaiagents import Agent, MCP
import ollama
import re
import multiprocessing
from dotenv import load_dotenv
import os
load_dotenv()  # Load variables from .env file



# def initialize_airbnb_agent():
#     return Agent(
#         instructions="""You are an Airbnb booking assistant. Your role is to help users find apartments and retrieve listing details on Airbnb.
# When a user asks for available apartments in a location, you should use the "airbnb_search" tool. The search tool requires parameters like:
#     - location: The city or area to search in.
#     - checkin and checkout: Dates for the stay.
#     - number of adults, children, infants, and optionally pets.
# When the user provides a specific listing ID or asks for more details about a listing, you should use the "airbnb_listing_details" tool. The details tool requires:
#     - id: The unique identifier for the listing.
#     - checkin and checkout dates (if applicable) along with guest information.
# Analyze the user's prompt carefully:
#     - If the prompt contains terms like “find”, “search”, “available”, or specifies a location and date range, choose the "airbnb_search" tool.
#     - If the prompt specifies a listing ID or asks for “details”, “information”, or “more about” a specific listing, use the "airbnb_listing_details" tool.
# If the user's prompt includes both a search and a detail request, decide the logical order: First perform a search to generate options, then retrieve the details for a specific listing.
# """,
#         llm="ollama/llama3.2:1b",
#         tools=MCP("npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt")
#     )

def initialize_airbnb_agent():
    return Agent(
        instructions="""You are a travel planning assistant that specializes in finding Airbnb listings and retrieving detailed information about specific properties. 
        Your goal is to help users effortlessly plan their trips by providing relevant and structured data—without requiring an API key.

        You can:
        - Use **airbnb_search** to find Airbnb listings based on filters like location, price range, and number of guests. Always include direct links to the listings.
        - Use **airbnb_listing_details** to get comprehensive details about a specific property, including pricing, amenities, reviews, and availability. Always include direct links to the listings.

        Use the tools wisely to assist users in making informed travel decisions while respecting Airbnb’s guidelines.
        """,
        llm="ollama/llama3.2:1b",
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
        llm="ollama/llama3.2:1b",
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
        """,
        llm="ollama/llama3.2:1b",
        tools=MCP("npx -y serper-search-scrape-mcp-server", env={"SERPER_API_KEY": serper_api_key})
    )

def initialize_github_agent():
    return Agent(
        instructions="You help with GitHub tasks and repository searches.",
        llm="ollama/llama3.2:1b",
        tools=MCP("npx -y @openbnb/mcp-server-github --ignore-robots-txt")
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
        "github": initialize_github_agent,
        "youtube": initialize_youtube_transcript_agent,
        "search": lambda: "search_agent",
        "get": lambda: "search_agent",
        "list": lambda: "search_agent"
    }

    for key, agent_initializer in keywords.items():
        if re.search(rf"\b{key}\b", query, re.IGNORECASE):
            if key in ["airbnb", "github", "google", "youtube"]:
                return run_agent_in_process(agent_initializer, query)
            else:
                return ollama.generate(model="llama3.2:1b", prompt=query)["response"]

    return ollama.generate(model="llama3.2:1b", prompt=query)["response"]
