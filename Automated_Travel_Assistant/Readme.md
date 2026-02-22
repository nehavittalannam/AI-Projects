# Multi-Agent Travel Support System using AutoGen & Azure OpenAI

**LLM-Orchestrated Swarm Architecture with Tool Calling & Intelligent Agent Handoffs**

An advanced multi-agent conversational AI system built using **Microsoft AutoGen Swarm framework** and **Azure OpenAI**, designed to simulate an enterprise-grade travel support automation system.

This system demonstrates agent collaboration, intelligent routing, tool usage, and termination control in a structured orchestration environment.

## Project Overview

This AI-powered system:

* Uses multiple specialized agents
* Implements intelligent agent-to-agent handoffs
* Enables tool execution (refund actions)
* Supports streaming conversation
* Tracks execution duration
* Maintains communication history
* Uses termination control logic

Designed to demonstrate **production-ready multi-agent orchestration patterns**.


## Architecture Overview

```text
User
  ↓
Travel Agent (Router / Orchestrator)
  ↓ ↓ ↓
Flights Refunder Agent
Car Refunder Agent
Generic Agent
  ↓
Tool Execution (Refund APIs)
  ↓
Finalization + Termination
```

## Agents in the System

### 1️⃣ Travel Agent (Orchestrator)

* Routes requests to appropriate agents
* Handles travel-related coordination
* Manages conversation flow
* Uses TERMINATE signal for completion

### 2️⃣ Flights Refunder Agent

* Specialized in flight refunds
* Uses `refund_flight()` tool
* Requests flight reference number if missing
* Returns control back to Travel Agent

### 3️⃣ Car Refunder Agent

* Handles car ride refunds
* Uses `refund_car()` tool
* Requests car reference ID if needed

### 4️⃣ Generic Agent

* Handles non-travel and general queries
* Uses LLM for knowledge-based responses
* Acts as fallback handler
* Hands control back for termination

## Tech Stack

* Python 3.x
* Microsoft AutoGen (Swarm Framework)
* Azure OpenAI
* Asyncio
* Tool Calling Architecture
* Agent Handoff Messaging
* Streaming Console Execution
* Structured Termination Control

## Key Architectural Concepts Demonstrated

### Multi-Agent Collaboration

Agents operate independently but collaborate via controlled handoffs.

### Tool Integration

Custom Python functions integrated as executable tools:

* `refund_flight(flight_id)`
* `refund_car(car_id)`

### Controlled Agent Routing

Uses:

* `HandoffMessage`
* `Swarm`
* `HandoffTermination`
* `TextMentionTermination`

### Streaming Execution

* Real-time interaction via `run_stream()`
* Asynchronous execution with `asyncio`

### Communication Logging

* Tracks entire conversation history
* Measures session duration
* Logs execution details

## 🔄 Conversation Flow Example

```text
User: I want to refund my flight.
Travel Agent → Flights Refunder
Flights Refunder: Please provide flight reference number.
User: FL12345
Flights Refunder → Tool Execution
Flight FL12345 refunded
Handoff → Travel Agent
TERMINATE
```

##  Installation

```bash
pip install autogen-agentchat
pip install autogen-ext
pip install openai
```

## Azure Configuration

Update:

```python
azure_deployment="your_deployment_name"
model="model_name"
api_version="version"
azure_endpoint="your_end_point"
api_key="your_api_key"
```

## ▶️ How to Run

```bash
python main.py
```

The system runs in streaming console mode and waits for user input dynamically.


## 🎯 Use Cases

* AI Customer Support Automation
* Refund & Ticketing Systems
* Enterprise Multi-Agent Systems
* Tool-Augmented LLM Applications
* Conversational Workflow Orchestration
* Agentic AI Demonstrations

## Author

**Neha V Annam**
AI & Data Engineer
