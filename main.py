import sys
from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, START, END

# --- 1. CONFIGURATION ---
# We use llama3.2 because it is fast for local testing
llm = ChatOllama(model="llama3.2", temperature=0)
search_tool = DuckDuckGoSearchRun()

# --- 2. DEFINE THE STATE ---
# This keeps track of what the agents know as they work
class SwarmState(TypedDict):
    competitor: str
    raw_data: str
    analysis: str
    iteration_count: int

# --- 3. DEFINE THE AGENT NODES ---

def researcher_node(state: SwarmState):
    """The Researcher Agent: Finds live data for free."""
    print(f"\n[Agent: Researcher] Finding data for {state['competitor']}...")
    
    query = f"Latest 2025-2026 market news and financial performance for {state['competitor']}"
    search_results = search_tool.run(query)
    
    return {
        "raw_data": search_results,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def analyst_node(state: SwarmState):
    """The Analyst Agent: Processes raw text into strategic insights."""
    print(f"[Agent: Analyst] Processing data locally...")
    
    prompt = f"""
    You are a Strategic Market Analyst. 
    Analyze the following raw data about {state['competitor']}:
    
    RAW DATA: {state['raw_data']}
    
    Provide a professional summary including:
    1. Key Financial Trends
    2. Main Competitive Threats
    3. Strategic Recommendation (Buy/Hold/Sell perspective)
    """
    
    response = llm.invoke(prompt)
    return {"analysis": response.content}

# --- 4. ORCHESTRATE THE GRAPH ---

workflow = StateGraph(SwarmState)

# Add our workers
workflow.add_node("researcher", researcher_node)
workflow.add_node("analyst", analyst_node)

# Define the workflow path
workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "analyst")
workflow.add_edge("analyst", END)

# Compile the application
app = workflow.compile()

# --- 5. EXECUTION ---

if __name__ == "__main__":
    target = input("Enter a competitor to research (e.g., NVIDIA, Tesla, Apple): ")
    
    initial_input = {
        "competitor": target,
        "raw_data": "",
        "analysis": "",
        "iteration_count": 0
    }
    
    print(f"\n🚀 Starting Swarm for {target}...\n")
    
    # Run the graph
    final_state = app.invoke(initial_input)
    
    print("\n" + "="*50)
    print(f"FINAL REPORT FOR {target.upper()}")
    print("="*50)
    print(final_state["analysis"])