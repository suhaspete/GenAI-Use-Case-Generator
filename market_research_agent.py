import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Skipping load_dotenv()")

# Import necessary libraries for agent creation
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain_community.tools.tavily_search import TavilySearchResults
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install required packages: pip install crewai langchain langchain-community")

# Set up API keys from environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OpenAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("Tavily_API_KEY")

# Initialize tools and create a list for the agents
try:
    # Initialize search tools
    search_tool = DuckDuckGoSearchRun()
    tavily_search = TavilySearchResults()

    # Create tools using the CrewAI tool decorator
    from crewai.tools import tool

    @tool("Search Tool")
    def search(query: str) -> str:
        """Useful for searching information about industries, companies, and market trends"""
        return search_tool.run(query)

    @tool("Tavily Search Tool")
    def tavily_search_tool(query: str) -> str:
        """Useful for detailed research on specific topics and finding recent information"""
        return tavily_search.run(query)

    # Create a list of tools for the agents
    tools = [search, tavily_search_tool]
except Exception as e:
    print(f"Error initializing tools: {e}")
    # Fallback to empty tools list if there's an error
    tools = []

# Define the Industry Research Agent
industry_research_agent = Agent(
    role="Industry Research Specialist",
    goal="Research and analyze the industry or company to understand its segment, key offerings, and strategic focus areas",
    backstory="You are an expert in market research with deep knowledge of various industries. Your specialty is analyzing industry trends and understanding company positioning within their markets.",
    verbose=True,
    allow_delegation=True,
    tools=tools,
    llm="gpt-3.5-turbo"
)

# Define the Use Case Generation Agent
use_case_generation_agent = Agent(
    role="AI Use Case Specialist",
    goal="Generate relevant AI and GenAI use cases based on industry research that can improve processes, enhance customer satisfaction, and boost operational efficiency",
    backstory="You are an AI solutions architect with expertise in applying AI technologies across different industries. You excel at identifying opportunities where AI can create significant business value.",
    verbose=True,
    allow_delegation=True,
    tools=tools,
    llm="gpt-3.5-turbo"
)

# Define the Resource Asset Collection Agent
resource_collection_agent = Agent(
    role="Resource Asset Collector",
    goal="Find relevant datasets and resources for implementing the proposed AI use cases",
    backstory="You are a data specialist who excels at finding and evaluating datasets from sources like Kaggle, HuggingFace, and GitHub. You know how to match business problems with appropriate data resources.",
    verbose=True,
    allow_delegation=True,
    tools=tools,
    llm="gpt-3.5-turbo"
)

# Define the tasks for each agent
industry_research_task = Task(
    description="""Research the specified industry or company and provide a comprehensive analysis including:
    1. The industry segment the company operates in
    2. Key offerings and products/services
    3. Strategic focus areas (operations, supply chain, customer experience, etc.)
    4. Current challenges and opportunities
    5. Competitive landscape

    If a specific company is provided, focus on that company. Otherwise, provide a general industry overview.

    Your final answer should be a structured report with clear sections and insights.
    """,
    agent=industry_research_agent,
    expected_output="A comprehensive industry or company analysis report"
)

use_case_generation_task = Task(
    description="""Based on the industry research provided, generate 10-15 relevant AI and GenAI use cases that can benefit the company or industry. For each use case:
    1. Provide a clear objective/problem statement
    2. Describe the AI application and how it addresses the problem
    3. Explain the cross-functional benefits across different departments
    4. Consider both operational efficiency and customer experience improvements
    5. Include GenAI solutions like document search, automated report generation, and AI-powered chat systems where applicable

    Your final answer should be a structured list of use cases with clear descriptions and benefits.
    """,
    agent=use_case_generation_agent,
    expected_output="A list of 10-15 AI and GenAI use cases with detailed descriptions"
)

resource_collection_task = Task(
    description="""For each of the proposed AI use cases, find relevant datasets and resources that could be used for implementation. Your research should include:
    1. Datasets from Kaggle, HuggingFace, GitHub, or other repositories
    2. Relevant research papers or articles
    3. Open-source tools or frameworks that could be leveraged
    4. Industry benchmarks or case studies

    Provide direct links to these resources and a brief description of how they relate to the use case.

    Your final answer should be a structured list of resources organized by use case.
    """,
    agent=resource_collection_agent,
    expected_output="A comprehensive list of datasets and resources for each use case"
)

# Create the crew with the agents and tasks
crew = Crew(
    agents=[industry_research_agent, use_case_generation_agent, resource_collection_agent],
    tasks=[industry_research_task, use_case_generation_task, resource_collection_task],
    verbose=True,  # Set verbose to True instead of 2
    process=Process.sequential,  # Tasks will be executed in sequence
    llm="gpt-3.5-turbo"  # Use gpt-3.5-turbo instead of the default gpt-4
)

def generate_use_cases(industry_or_company: str) -> Dict[str, Any]:
    """Generate AI use cases for a specific industry or company.

    Args:
        industry_or_company: The name of the industry or company to research

    Returns:
        A dictionary containing the research results, use cases, and resources
    """
    print(f"Generating AI use cases for: {industry_or_company}")

    # Update the task descriptions with the specific industry or company
    industry_research_task.description = industry_research_task.description.replace(
        "the specified industry or company", f"\"{industry_or_company}\""
    )

    # Run the crew to execute all tasks
    result = crew.kickoff()

    # Parse and structure the results
    # Handle different result formats from CrewAI
    try:
        # Try accessing results as a list (older CrewAI versions)
        results_dict = {
            "industry_research": result[0],
            "use_cases": result[1],
            "resources": result[2]
        }
    except (IndexError, TypeError):
        # Handle newer CrewAI versions that might return a different structure
        print("Using alternative result parsing method")
        # Get the results from the tasks directly
        results_dict = {
            "industry_research": industry_research_task.output if hasattr(industry_research_task, 'output') else "No research data available",
            "use_cases": use_case_generation_task.output if hasattr(use_case_generation_task, 'output') else "No use cases available",
            "resources": resource_collection_task.output if hasattr(resource_collection_task, 'output') else "No resources available"
        }

    # Create reports directory if it doesn't exist
    import os
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        print(f"Created directory: {reports_dir}")

    # Generate a timestamp for unique filenames
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a subdirectory for this specific report
    report_subdir = os.path.join(reports_dir, f"{industry_or_company.replace(' ', '_')}_{timestamp}")
    os.makedirs(report_subdir)

    # Save results to files in the reports directory
    research_path = os.path.join(report_subdir, "research.md")
    with open(research_path, "w") as f:
        f.write(f"# Industry Research: {industry_or_company}\n\n")
        f.write(results_dict["industry_research"])

    use_cases_path = os.path.join(report_subdir, "use_cases.md")
    with open(use_cases_path, "w") as f:
        f.write(f"# AI Use Cases for {industry_or_company}\n\n")
        f.write(results_dict["use_cases"])

    resources_path = os.path.join(report_subdir, "resources.md")
    with open(resources_path, "w") as f:
        f.write(f"# Resources for {industry_or_company} AI Implementation\n\n")
        f.write(results_dict["resources"])

    # Create a summary file with links to all reports
    summary_path = os.path.join(report_subdir, "summary.md")
    with open(summary_path, "w") as f:
        f.write(f"# AI Use Case Summary for {industry_or_company}\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Reports:\n\n")
        f.write(f"- [Industry Research](research.md)\n")
        f.write(f"- [AI Use Cases](use_cases.md)\n")
        f.write(f"- [Implementation Resources](resources.md)\n")

    print(f"Results saved to directory: {report_subdir}")
    return results_dict

if __name__ == "__main__":
    # Example usage
    industry_or_company = input("Enter the industry or company name to research: ")
    results = generate_use_cases(industry_or_company)