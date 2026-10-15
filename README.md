# AI SRE Incident Agent for Smart Electricity System

An agentic AI-based Site Reliability Engineering (SRE) assistant that monitors, investigates, and explains incidents in a Smart Electricity microservice environment.

The project combines:

- Real microservices
- Python diagnostic tools
- LangChain tool calling
- OpenRouter-hosted LLMs
- Service health monitoring
- TCP/port diagnostics
- Log analysis
- Dependency checking
- Real MySQL authentication testing
- AI-assisted incident investigation

The agent is currently **read-only**. It can investigate problems and recommend actions, but it does not automatically restart services or modify system configuration.

---

# 1. Project Overview

The Smart Electricity System consists of several independent microservices.

The AI SRE Incident Agent sits outside those services and monitors them.

Instead of asking an LLM to guess what is wrong, the agent is provided with real diagnostic tools.

The AI decides which tools it needs to use based on the problem being investigated.

Example:

```text
User:
Investigate the whole system

        ↓

LangChain SRE Agent

        ↓

Check all services

        ↓

Billing Service unreachable

        ↓

Check Billing port

        ↓

Port 3001 closed

        ↓

Read Billing logs

        ↓

Check Billing dependencies

        ↓

Test MySQL authentication

        ↓

Correlate all evidence

        ↓

Generate incident report