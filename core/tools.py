from duckduckgo_search import DDGS
from langchain.tools import tool
from utils.logger import logger
@tool 
def search_merchant(query: str) -> str:
    """
    Searches the web for information about an unknown merchant, charge description, or financial term found in a statement.
    Use this when you see an unfamiliar merchant name or charge description that needs external context to explain.
    Args:
        query: merchant name or charge description to search for
    Returns:
        A summary string of the top search results
    """

    try:
        logger.info(f"Searching for merchants: {query}")
        results = []
        with DDGS() as ddgs:
            search_query = f"{query} charge explanation bank statement"
            hits = ddgs.text(search_query, max_results=3)
            for hit in hits:
                results.append(f"- {hit['title']}: {hit['body']}")
            if not results:
                return f"No search results found for '{query}'."

        return "\n".join(results)
    except Exception as e:
        logger.info(f"Search unavailable right now: {str(e)}")
        return f"Search unavailable right now: {str(e)}"
        