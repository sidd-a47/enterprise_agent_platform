# Enterprise Agent Platform

A lightweight multi-agent orchestration system built with Python and Groq (Llama 3.3).

## What it does

The Orchestrator Agent receives a user request, classifies it into one of three categories, and routes it accordingly:

- **Calculation** → Uses a built-in calculator tool
- **Factual** → Delegates to a specialist Retrieval Agent
- **Chat** → Handles the conversation directly

All requests pass through basic safety guardrails before and after processing.

## Architecture