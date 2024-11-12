# Overview

Automating some task of Site Reliable Engineer (SREs) for ML pipeline:

- With multiple monitoring data and stream, I will use LLM to analyse the root cause when the SLA is violated, mainly will deal with latency and throughput here
- Then, the LLM will suggest some mitigation. Depending on my progress, the mitigation maybe automatic or will require human intervention
- Application structure: dependency, ...
  List of LLM to test:
- Phi 3.5
- Chat GPT 3.5 4 4o
- Llama

# Study questions

- Different LLM can return different analysis and mitigation and the context size really matter as the monitoring data can be quite big -> _Evaluate the quality of LLM's output manually to see which size is reasonable_ for this task because obviously the bigger the LLM, the better the result but the increased cost may not justify this increase in performance. List of problems that I will test:
  - Increased latency
  - Reduced throughput
- _Testing in 2 scenarios to see if the profiling data increase the RCA quality_ of LLM's output:
  - Without profiling data
  - With profiling data

# Assumption

- Applications: the object classification ML pipeline from the tutorials
- Environment: local k8s cluster
- Observability data considered here is trace, metric, and profiling. I don't consider the logs here because implementing a good logging int he application can take time
- Observability and SLA are implemented/defined similar to the tutorial

# Current state

- Application is already implemented
- Next week:
  - Deploying one LLM locally and test it in above scenarios
  - Figure out how to feed data to LLM
  - Adding continuous profiling to the ML pipeline
- Next next week:
  - Testing with other LLM
  - Testing with/without profiling data to see the performance
