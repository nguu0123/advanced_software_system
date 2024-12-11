# Why 
The context length of an LLm model is limited (Llama 3 has 4096 token context length) so with long context or conversation, the LLM will not be able to retain the previous performance 
# How 
1. Truncate previous messages 
2. Summarize previous message