## Techniques 
- [[Zero-shot prompting]]: directly prompt the model for a response without any examples or demonstrations about the task. Can be format as:
```
Q: <Question>?
A: 
```
- [[Few-shot prompting]]: provide exemplars or demonstrations which help the models to learn tasks in-context. Example is:
```
<Question>?
<Answer>
<Question>?
<Answer>
<Question>?
<Answer>
<Question>?
```
- [[Chain-of-thought]]: 
- [[Meta prompting]]
- [[Prompt chaining]]
- [[Self-Consistency]]
- [[Generate Knowledge Prompting]]
- [[Tree of Thoughts]]
- [[Retrieval Augmented Generation (RAG)]]
- [[Automatic Reasoning and Tool-use]]
- [[Automatic Prompt Engineer]]
- [[Active-Prompt]]
- [[Program-Aided Language Models]]: use LLms to read natural language problems and generate programs as the intermediate reasoning steps 
- [[ReAct Prompting]]: LLms are used to generate both *reasoning traces* and *task-specific* in an interleaved manner
## Elements of a good prompt 
A prompt contains any of the following elements:
- *Instruction*: a specific task or instruction
- *Context*: external information or additional context that can steer the model to better responses 
- *Input Data*: the input or question that we're interested 
- *Output Indicator*: type or format of output