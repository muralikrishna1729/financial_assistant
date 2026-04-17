from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
from core.tools import search_merchant
from utils.logger import logger
import os

load_dotenv()

SYSTEM_PROMPT = """
You are a Financial Document Assistant. Your job is to help users 
understand charges, transactions, and summaries in their financial 
documents such as credit card statements, invoices, and receipts.

You have been given the extracted content of the uploaded document 
in markdown format below. Always base your answers on this document.

--- DOCUMENT CONTENT START ---
{document_context}
--- DOCUMENT CONTENT END ---

Follow these rules strictly:

1. GROUND YOUR ANSWER: Every amount or date you mention must come 
   directly from the document above. Never invent numbers.

2. USE SEARCH WHEN NEEDED: If a merchant name or charge description 
   is unclear or unfamiliar, use the search_merchant tool to look it up
   before answering. Do not guess.

3. CITE YOUR SOURCE: When mentioning a specific amount, always say 
   where you found it. Example: "According to your statement, the 
   charge of $320.45 was for Amazon Web Services EC2 Usage."

4. MATH VERIFICATION: If the user asks about totals or balances, 
   add up the line items yourself and confirm it matches the document.

5. STAY IN SCOPE: Only answer questions related to the financial 
   document. If asked something unrelated, politely decline.

6. BE CONCISE: Give clear, direct answers. No unnecessary filler.
"""


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        streaming=True
    )


def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])


def build_agent(document_context: str):
    llm = get_llm()
    prompt = get_prompt().partial(document_context=document_context)
    tools = [search_merchant]
    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=4,
        handle_parsing_errors=True
    )


def stream_agent_response(agent_executor, user_question, chat_history):
    inputs = {
        "input": user_question,
        "chat_history": chat_history
    }

    try:
        for event in agent_executor.stream(inputs):
            if "actions" in event:
                for action in event["actions"]:
                    logger.info(f"Agent calling tool: {action.tool} | input: {action.tool_input}")
            elif "steps" in event:
                for step in event["steps"]:
                    logger.info(f"Tool result from: {step.action.tool}")

            if "output" in event:
                words = event["output"].split(" ")
                for word in words:
                    yield word + " "

    except Exception as e:
        logger.error(f"Streaming error: {str(e)}", exc_info=True)
        yield "I encountered an error while processing your request."