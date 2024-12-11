import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

system_template_ver1 = "Acting as an On-call Engineering"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template_ver1), ("user", "{text}")]
)
model = ChatOllama(model="phi3", temperature=0.2, num_ctx=4096)


trace_path = os.path.join(os.getcwd(), "traces", "normal-traces-minified-1.json")
with open(trace_path) as file:
    normal_trace_1 = file.readline()


trace_path = os.path.join(os.getcwd(), "traces", "spiked-traces-minified-1.json")
with open(trace_path) as file:
    spiked_trace_1 = file.readline()


prompt_ver1 = prompt_template.invoke(
    {
        "text": f"The following is a trace of a normal request:\n{normal_trace_1}\nThe following is a trace of a request that has spiked latency\n{spiked_trace_1}\nCompare those two trace to see which service is the root cause of the spiked latency"
    }
)

for chunk in model.stream(prompt_ver1):
    print(chunk.content, end="", flush=True)
