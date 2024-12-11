import getpass
import os
import sys
from io import StringIO
from typing import Literal

from langchain.tools import Tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

os.environ["LANGCHAIN_TRACING_V2"] = "true"

if not os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


class PythonREPL:
    """Simulates a standalone Python REPL."""

    def __init__(self):
        pass

    def run(self, command: str) -> str:
        """Run command and return anything printed."""
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command, globals())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            output = str(e)
        return output


python_repl_tool = Tool(
    name="PythonREPL",
    func=PythonREPL().run,
    description="""A Python shell. Use this to execute python commands. Input should be a valid python command. If you expect output it should be printed out.""",
)
tools = [python_repl_tool]

tool_node = ToolNode(tools)

model = ChatOllama(model="llama3.2", temperature=0.2).bind_tools(tools)

# model = ChatOpenAI(
#     model="gpt-4o",
#     temperature=0.2,
#     max_retries=1,
# ).bind_tools(tools)


def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
)

workflow.add_edge("tools", "agent")

checkpointer = MemorySaver()

app = workflow.compile()

trace_path = os.path.join(os.getcwd(), "traces", "normal-traces-minified-1.json")
with open(trace_path) as file:
    normal_trace_1 = file.readline()


trace_path = os.path.join(os.getcwd(), "traces", "spiked-traces-minified-1.json")
with open(trace_path) as file:
    spiked_trace_1 = file.readline()

human_message = HumanMessage(
    content=f"The following is a trace of a normal request:\n{normal_trace_1}\nThe following is a trace of a request that has spiked latency\n{spiked_trace_1}\nCompare those two trace to see which service is the root cause of the spiked latency"
)
# print(human_message.content)
for event in app.stream(
    {"messages": [human_message]},
):
    for value in event.values():
        for message in value["messages"]:
            print("Assistant:", message.content)
