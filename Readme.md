

python -m streamlit run app.py

create a generic helper that abstracts the process creation and call for any MCP-based agent. Then, simply map each keyword to its agent initializer and use that helper

The code uses Python’s multiprocessing to spawn a worker process that creates the Airbnb agent and executes the start command, then returns the result via a queue.

# normal air
Book for apartments in Paris for 2 nights. 20/05/2025 - 22/05/2025 for 1 adult, max 50€ in 1 night, give me the name, id of airbnb, address and cost

# airbnb_search
# use: airbnb_listing_details, I want to get detailed information from this Airbnb place id= 1073969258803632789



s