# DineVoice — Production-Grade AI Voice Agent for Restaurant Food Ordering

> A production-grade, real-time AI voice agent that allows customers to **order food directly from a restaurant using natural voice conversations**.

DineVoice acts as an AI-powered restaurant phone assistant. Customers can ask about the menu, customize dishes, add items to their cart, confirm their order, provide delivery details, and place an order — all through a natural voice conversation.

The project focuses not only on conversational AI, but also on **real-time voice processing, agentic workflows, RAG, tool calling, latency optimization, reliability, observability, evaluation, and production deployment**.

---

## 🎯 Problem

Restaurants often receive a large number of phone calls for:

- Food ordering
- Menu questions
- Item availability
- Price inquiries
- Customization requests
- Delivery information
- Order status
- Order cancellation

Handling these calls manually can be expensive and difficult to scale, especially during peak hours.

DineVoice aims to automate this process with an AI voice agent that can understand customers and interact with the restaurant's ordering system.

---

# 🚀 What DineVoice Does

A customer can call the restaurant and have a conversation such as:

> **Customer:** Hi, I'd like to order two chicken burgers and one fries.

> **AI:** Sure. Would you like the burgers with the regular or spicy sauce?

> **Customer:** One regular and one spicy.

> **AI:** Got it. I've added two chicken burgers and one fries to your cart. Your current total is ₹420. Would you like to add a drink?

> **Customer:** Yes, add one Coke.

> **AI:** Done. Your total is now ₹470. Would you like delivery or pickup?

The agent then collects the required information, confirms the complete order, and places it through the restaurant's ordering backend.

---

# 🧠 Core Capabilities

### Voice Ordering

Customers can place complete food orders using natural speech.

- Understand natural language
- Handle different accents and speaking styles
- Understand quantities
- Understand food names
- Handle corrections
- Handle follow-up questions
- Maintain conversation context

### Menu Discovery

Customers can ask:

- "What pizzas do you have?"
- "Do you have vegetarian burgers?"
- "What's the cheapest meal?"
- "What comes with the chicken combo?"
- "Do you have anything spicy?"

The agent retrieves relevant menu information before responding.

### Food Customization

The agent can understand requests such as:

- No onions
- Extra cheese
- Less spicy
- Add sauce
- Remove tomato
- Extra toppings
- Make it vegetarian
- Change size

### Cart Management

Customers can:

- Add items
- Remove items
- Change quantity
- Modify customizations
- Review their cart
- Start over

### Order Placement

Before placing an order, the agent confirms:

- Items
- Quantities
- Customizations
- Subtotal
- Taxes
- Delivery charges
- Discounts
- Final amount
- Delivery/pickup method
- Customer information

The order is only submitted after explicit confirmation.

### Order Status

Customers can ask:

> "Where is my order?"

> "Has my order been prepared?"

> "When will it arrive?"

The agent can retrieve order information from the restaurant's backend.

### Human Handoff

The agent can transfer the conversation to a human when:

- Customer explicitly requests an employee
- The request is outside the supported workflow
- The system cannot confidently understand the order
- Payment/order processing fails
- The customer has a complex complaint

---

# 🏗️ System Architecture

```text
                         CUSTOMER
                            │
                            │ Phone / Voice
                            ▼
                    ┌─────────────────┐
                    │     LiveKit     │
                    │ WebRTC / Audio  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Voice Activity │
                    │   Detection     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │       STT       │
                    │ Speech → Text   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   LangGraph     │
                    │  Agent Workflow │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐   ┌────────────┐   ┌───────────┐
        │   RAG    │   │   Tools    │   │   State   │
        │  Qdrant  │   │ Order API  │   │  Memory   │
        └──────────┘   └────────────┘   └───────────┘
              │              │              │
              ▼              ▼              ▼
        ┌─────────────────────────────────────────┐
        │       Restaurant Backend / Database     │
        │                                         │
        │ Menu │ Inventory │ Cart │ Orders │ User │
        └────────────────────┬────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │       LLM       │
                    │ Reasoning / NLU │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │       TTS       │
                    │ Text → Speech   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     LiveKit     │
                    │ Streaming Audio │
                    └────────┬────────┘
                             │
                             ▼
                         CUSTOMER
```

---

# 🛠️ Tech Stack

## AI / LLM

- Python
- Gemini 3.8 flash
- Open-source LLMs
- Hugging Face Transformers
- LangGraph
- LangChain
- Pydantic
- Structured Outputs
- Function / Tool Calling

---

## 🎙️ Voice AI

- LiveKit
- WebRTC
- Streaming audio
- Speech-to-Text (STT)
- Text-to-Speech (TTS)
- Voice Activity Detection (VAD)
- Audio streaming
- Interruption / Barge-in handling

---

## 🧠 Agent Architecture

- LangGraph
- Stateful workflows
- Tool calling
- Conditional routing
- Agent state
- Short-term conversation memory
- Retry mechanisms
- Fallback strategies
- Human-in-the-loop
- Structured tool execution

---

## 📚 RAG

- Embedding models
- Qdrant
- Vector similarity search
- Metadata filtering
- Hybrid retrieval
- Reranking
- Context compression

### Knowledge Base

The RAG system can contain:

```text
Restaurant Information
├── Menu
│   ├── Categories
│   ├── Items
│   ├── Ingredients
│   ├── Prices
│   └── Customizations
│
├── Dietary Information
│   ├── Vegetarian
│   ├── Vegan
│   ├── Allergens
│   └── Dietary restrictions
│
├── Restaurant Policies
│   ├── Delivery areas
│   ├── Minimum order
│   ├── Cancellation policy
│   └── Refund policy
│
└── FAQs
    ├── Opening hours
    ├── Delivery time
    ├── Payment methods
    └── Contact information
```

---

# 🍔 Food Ordering Tools

The AI agent interacts with the restaurant backend through controlled tools.

```text
get_menu()

search_menu(query)

get_item_details(item_id)

check_item_availability(item_id)

add_to_cart(
    item_id,
    quantity,
    customizations
)

remove_from_cart(item_id)

update_cart_item(
    item_id,
    quantity
)

get_cart()

calculate_order_total()

apply_coupon(code)

create_order()

get_order_status(order_id)

cancel_order(order_id)

transfer_to_human()
```

The LLM does **not directly modify the database**.

Instead:

```text
LLM
 │
 ▼
Structured Tool Call
 │
 ▼
Validation
 │
 ▼
Backend API
 │
 ▼
Database
```

This provides better control, validation, and reliability.

---

# 🔄 Order Flow

```text
Customer starts conversation
            │
            ▼
      Understand intent
            │
            ▼
       Search menu
            │
            ▼
    Check availability
            │
            ▼
     Add items to cart
            │
            ▼
  Handle customizations
            │
            ▼
      Review cart
            │
            ▼
   Calculate final price
            │
            ▼
 Collect delivery / pickup details
            │
            ▼
      Confirm order
            │
            ▼
       Create order
            │
            ▼
      Order ID generated
            │
            ▼
     Confirmation to user
```

---

# 🧩 Agent State

The agent maintains structured state throughout the conversation.

Example:

```json
{
  "customer": {
    "name": "Rahul",
    "phone": "XXXXXXXXXX"
  },
  "order_type": "delivery",
  "cart": [
    {
      "item": "Chicken Burger",
      "quantity": 2,
      "customizations": ["No onions", "Extra cheese"]
    }
  ],
  "delivery_address": "...",
  "subtotal": 400,
  "delivery_fee": 40,
  "tax": 22,
  "total": 462,
  "order_status": "awaiting_confirmation"
}
```

The state is controlled by the application rather than relying entirely on the LLM's conversational memory.

---

# ⚡ Real-Time Voice Pipeline

The system is designed around streaming rather than waiting for an entire conversation turn to finish.

```text
Customer Speech
      │
      ▼
 Audio Stream
      │
      ▼
     VAD
      │
      ▼
 Streaming STT
      │
      ▼
 Partial Transcript
      │
      ▼
 LangGraph / LLM
      │
      ▼
 Streaming Response
      │
      ▼
 Streaming TTS
      │
      ▼
 Audio Stream
      │
      ▼
 Customer
```

The objective is to reduce perceived latency and make the conversation feel natural.

---

# ⏱️ Latency Engineering

Latency is one of the primary engineering goals of DineVoice.

Important measurements include:

| Metric                      | Target |
| --------------------------- | -----: |
| STT latency                 |    TBD |
| LLM Time To First Token     |    TBD |
| TTS Time To First Audio     |    TBD |
| End-to-End Response Latency |    TBD |
| Tool Execution Latency      |    TBD |
| First Audio Response        |    TBD |

Actual benchmark values will be added after implementation and testing.

---

# 🚀 Latency Optimization

Potential optimization techniques:

### Streaming

Stream:

- Audio input
- STT output
- LLM tokens
- TTS audio

instead of waiting for complete responses.

### Model Selection

Compare different models based on:

- Latency
- Accuracy
- Cost
- Context length
- Tool-calling reliability

### Prompt Optimization

Reduce unnecessary:

- System prompt size
- Retrieved context
- Tool descriptions
- Conversation history

### Retrieval Optimization

Use:

- Metadata filtering
- Top-K tuning
- Reranking
- Context compression

### Inference Optimization

For self-hosted models, experiment with:

- FP16
- BF16
- INT8
- INT4
- KV cache
- Continuous batching
- vLLM

---

# 🤖 Model Benchmarking

Different model configurations can be compared.

```text
                    Model Benchmark
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
      Quality           Latency            Cost
        │                 │                 │
        ▼                 ▼                 ▼
   Tool accuracy      TTFT / E2E       Cost / call
   Order accuracy     P50/P95          Cost / session
   RAG accuracy       TTFB             Monthly estimate
```

Example benchmark table:

| Model   | Tool Accuracy | TTFT | E2E Latency | Cost/Call |
| ------- | ------------: | ---: | ----------: | --------: |
| Model A |           TBD |  TBD |         TBD |       TBD |
| Model B |           TBD |  TBD |         TBD |       TBD |
| Model C |           TBD |  TBD |         TBD |       TBD |

Only measured results will be documented here.

---

# 📊 RAG Evaluation

The RAG system will be evaluated independently.

Metrics may include:

- Retrieval precision
- Retrieval recall
- Hit@K
- MRR
- Context relevance
- Answer faithfulness
- Groundedness
- Hallucination rate

Example evaluation flow:

```text
Question
   │
   ▼
Retriever
   │
   ▼
Retrieved Documents
   │
   ▼
Reranker
   │
   ▼
LLM
   │
   ▼
Generated Answer
   │
   ▼
Evaluation
```

---

# 🔧 Agent Evaluation

The agent will also be evaluated on its ability to correctly execute restaurant workflows.

Important evaluation cases:

### Intent Detection

```text
"Show me vegetarian options"
→ MENU_SEARCH
```

```text
"I want to order two pizzas"
→ CREATE_ORDER
```

```text
"Where is my order?"
→ ORDER_STATUS
```

### Tool Selection

Measure whether the correct tool is selected.

### Tool Arguments

Verify:

- Item ID
- Quantity
- Customizations
- Order ID
- Customer information

### Workflow Correctness

Verify that the agent follows the correct sequence.

For example:

```text
Search Item
      ↓
Check Availability
      ↓
Add To Cart
      ↓
Calculate Total
      ↓
Confirm
      ↓
Create Order
```

The agent should not skip critical validation steps.

---

# 🛡️ Reliability & Safety

Food ordering requires deterministic backend validation.

The system should protect against:

- Invalid item IDs
- Incorrect quantities
- Unavailable items
- Incorrect prices
- Invalid coupons
- Duplicate orders
- Incorrect totals
- Invalid delivery addresses
- Accidental order creation

### Important Principle

> The LLM can decide **what it wants to do**, but the backend decides **what is actually allowed**.

For example:

```text
LLM:
"Add 5 Chicken Burgers"

        ↓

Backend Validation

        ↓

Is item available?
Is quantity valid?
Is customization valid?
Is price current?

        ↓

Database Operation
```

---

# 💳 Payment Architecture

The initial version can support:

```text
Cash on Delivery
Online Payment
Pay at Pickup
```

For online payment, the architecture should avoid allowing the LLM to directly handle payment credentials.

Instead:

```text
Customer
   │
   ▼
AI Agent
   │
   ▼
Create Pending Order
   │
   ▼
Payment Gateway
   │
   ▼
Payment Confirmation
   │
   ▼
Order Confirmed
```

Sensitive payment information should be handled by the payment provider rather than the LLM.

---

# 👤 Human Handoff

The agent should be able to transfer a conversation to a restaurant employee.

Possible triggers:

```text
Customer requests human
        OR
Low confidence
        OR
Complex complaint
        OR
Payment failure
        OR
Unsupported request
```

Before transferring, the system can provide the human agent with:

```text
Customer
Current cart
Order ID
Conversation summary
Issue
Previous tool calls
```

---

# 🧪 Testing

## Unit Testing

- Tool functions
- Cart calculations
- Order validation
- API endpoints
- RAG components
- State transitions

Technology:

```text
Pytest
```

---

## Integration Testing

Test complete workflows:

```text
Voice
 ↓
STT
 ↓
Agent
 ↓
Tool
 ↓
Database
 ↓
TTS
```

---

## Load Testing

Use:

```text
Locust
```

Test progressively:

```text
1 concurrent call
       ↓
10 concurrent calls
       ↓
50 concurrent calls
       ↓
100 concurrent calls
       ↓
500+ concurrent calls
```

Measure:

- Requests/sec
- Concurrent sessions
- P50 latency
- P95 latency
- P99 latency
- Error rate
- CPU utilization
- RAM usage
- GPU utilization
- Database latency
- Model throughput

Actual capacity numbers will be documented only after real load testing.

---

# 📈 Observability

The system should provide visibility into every important stage.

```text
Call
 │
 ├── STT
 │
 ├── Agent
 │    ├── Intent
 │    ├── Retrieval
 │    ├── Tool Selection
 │    └── Tool Execution
 │
 ├── Database
 │
 └── TTS
```

Track:

- Request ID
- Call/session ID
- User intent
- Tool calls
- Tool latency
- LLM latency
- STT latency
- TTS latency
- Retrieval latency
- Errors
- Fallbacks
- Human handoffs

Technologies:

- Structured logging
- OpenTelemetry
- CloudWatch
- Metrics
- Distributed tracing

---

# ☁️ AWS Deployment

Target deployment architecture:

```text
                    Internet
                       │
                       ▼
                 AWS Load Balancer
                       │
                       ▼
                FastAPI Application
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
      LangGraph      Redis       PostgreSQL
          │
          ▼
        Qdrant
          │
          ▼
      LLM Service
          │
          ▼
      Voice Services
```

Potential AWS services:

- EC2
- ECS
- S3
- Application Load Balancer
- CloudWatch
- IAM
- VPC
- Redis
- PostgreSQL

Docker will be used to package application components.

---

# 🐳 Containerization

Example services:

```text
docker-compose.yml

services:

  api
  worker
  postgres
  redis
  qdrant
  monitoring
```

The architecture should allow individual services to be scaled independently where required.

---

# 📁 Project Structure

```text
dinevoice/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   └── tools/
│   │
│   ├── voice/
│   │   ├── stt/
│   │   ├── tts/
│   │   ├── vad/
│   │   └── livekit/
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   ├── retrieval/
│   │   ├── reranking/
│   │   └── embeddings/
│   │
│   ├── ordering/
│   │   ├── cart.py
│   │   ├── orders.py
│   │   └── validation.py
│   │
│   ├── models/
│   ├── database/
│   ├── services/
│   └── config/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── evaluation/
│   └── load/
│
├── scripts/
│   ├── ingestion/
│   ├── benchmarking/
│   └── evaluation/
│
├── docker/
│
├── docs/
│   ├── architecture.md
│   ├── evaluation.md
│   └── benchmarks.md
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🗄️ Database

### PostgreSQL

Potential tables:

```text
restaurants
menu_categories
menu_items
item_customizations
customers
carts
cart_items
orders
order_items
payments
order_events
```

Example order lifecycle:

```text
CART
  ↓
PENDING_CONFIRMATION
  ↓
CONFIRMED
  ↓
PREPARING
  ↓
READY
  ↓
OUT_FOR_DELIVERY
  ↓
DELIVERED
```

---

# 🔎 Vector Database

Qdrant will store embeddings for unstructured restaurant information.

Example metadata:

```json
{
  "restaurant_id": "restaurant_123",
  "category": "menu",
  "item_id": "burger_42",
  "dietary_type": "vegetarian"
}
```

Metadata filtering allows the agent to retrieve information specific to the correct restaurant or menu category.

---

# 🧠 Model Engineering

The project can include experiments with open-source models.

Potential technologies:

- Hugging Face Transformers
- PyTorch
- PEFT
- LoRA
- QLoRA
- Quantization
- FP16
- BF16
- INT8
- INT4
- vLLM

The goal is to understand the complete path:

```text
Model
  ↓
Fine-tuning
  ↓
Quantization
  ↓
Model Serving
  ↓
Inference
  ↓
Latency / Throughput
  ↓
Production
```

---

# 🔬 Fine-Tuning Experiment

A small domain-specific fine-tuning experiment may be added for tasks such as:

- Restaurant intent classification
- Tool selection
- Structured order extraction
- Food customization extraction

Example:

```text
Customer:
"Give me two paneer pizzas, one without onions."

        ↓

Model

        ↓

{
  "items": [
    {
      "name": "paneer pizza",
      "quantity": 2,
      "customizations": [
        "no onions"
      ]
    }
  ]
}
```

The experiment will compare:

```text
Base Model
     vs
Fine-Tuned Model
```

using accuracy, latency, and reliability metrics.

---

# ⚙️ Performance Engineering

Areas investigated:

- Streaming inference
- Async processing
- Connection pooling
- Redis caching
- Database indexing
- Vector search optimization
- Reranking optimization
- LLM prompt optimization
- Token reduction
- Model quantization
- vLLM inference
- Concurrent request handling

---

# 📊 Production Metrics

The project will track:

### Voice

- Speech recognition accuracy
- Time to first audio
- End-to-end latency
- Interruption handling

### Agent

- Intent accuracy
- Tool selection accuracy
- Tool argument accuracy
- Workflow completion rate

### RAG

- Retrieval recall
- Retrieval precision
- Hit@K
- MRR
- Groundedness

### Ordering

- Order extraction accuracy
- Cart accuracy
- Price calculation accuracy
- Order success rate
- Duplicate order rate

### Infrastructure

- CPU
- Memory
- GPU
- Throughput
- P50 latency
- P95 latency
- P99 latency
- Error rate

---

# 🗺️ Development Roadmap

## Phase 1 — Voice Foundation

- [ ] Set up LiveKit
- [ ] Integrate STT
- [ ] Integrate TTS
- [ ] Implement basic voice conversation
- [ ] Implement VAD
- [ ] Test streaming audio

---

## Phase 2 — Agent

- [ ] Build LangGraph workflow
- [ ] Define agent state
- [ ] Add intent detection
- [ ] Add structured outputs
- [ ] Add tool calling
- [ ] Add retry/fallback handling

---

## Phase 3 — Restaurant Ordering

- [ ] Restaurant database
- [ ] Menu API
- [ ] Menu search
- [ ] Item availability
- [ ] Cart management
- [ ] Customizations
- [ ] Price calculation
- [ ] Order creation
- [ ] Order status
- [ ] Cancellation

---

## Phase 4 — RAG

- [ ] Document ingestion
- [ ] Embeddings
- [ ] Qdrant
- [ ] Metadata filtering
- [ ] Reranking
- [ ] Context compression
- [ ] Retrieval evaluation

---

## Phase 5 — Real-Time Optimization

- [ ] Streaming STT
- [ ] Streaming LLM
- [ ] Streaming TTS
- [ ] Barge-in
- [ ] Measure TTFT
- [ ] Measure end-to-end latency
- [ ] Optimize prompts
- [ ] Optimize retrieval

---

## Phase 6 — Model Engineering

- [ ] Hugging Face Transformers
- [ ] Open-source model testing
- [ ] Quantization
- [ ] LoRA
- [ ] QLoRA
- [ ] vLLM
- [ ] Inference benchmarking

---

## Phase 7 — Production

- [ ] Docker
- [ ] AWS deployment
- [ ] PostgreSQL
- [ ] Redis
- [ ] Logging
- [ ] Metrics
- [ ] Tracing
- [ ] Error handling
- [ ] Load testing
- [ ] Autoscaling

---

# 🧪 Final Evaluation

The final system should be evaluated using realistic conversations.

Example:

```text
Customer:
"Hi, I want two large chicken pizzas."

AI:
"Sure. Would you like any toppings or customizations?"

Customer:
"Add extra cheese to one and no onions on the other."

AI:
"Got it."

Customer:
"Also add one Coke."

AI:
"Done. Your cart has two large chicken pizzas and one Coke.
The first pizza has extra cheese and the second has no onions.
Your total is ₹XXX. Would you like delivery or pickup?"

Customer:
"Delivery."

AI:
"Please provide your delivery address."

Customer:
"[Address]"

AI:
"Your total is ₹XXX including delivery.
Should I place the order?"

Customer:
"Yes."

AI:
"Your order has been placed successfully.
Your order ID is #12345."
```

The evaluation should verify:

- Correct item recognition
- Correct quantity
- Correct customization
- Correct cart state
- Correct price
- Correct tool sequence
- Correct order creation
- Correct final response
- No hallucinated menu items
- No incorrect pricing
- No accidental order submission

---

# 🎯 Engineering Goals

DineVoice is designed to demonstrate practical AI engineering skills across the entire stack:

```text
                DineVoice
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
    Voice AI      Agent AI      RAG
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
             AI Engineering
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
   Inference    Evaluation    Backend
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼
               Production
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      AWS        Monitoring     Scaling
```

---

# 💡 What This Project Demonstrates

DineVoice demonstrates experience with:

- Real-time voice AI
- Speech-to-text
- Text-to-speech
- WebRTC
- LiveKit
- LLM applications
- LangGraph
- Agentic workflows
- Tool calling
- Stateful agents
- RAG
- Vector databases
- Reranking
- Structured outputs
- Backend API design
- PostgreSQL
- Redis
- Async Python
- Model benchmarking
- LLM evaluation
- Latency engineering
- Model quantization
- LoRA / QLoRA
- vLLM
- Docker
- AWS
- Observability
- Load testing
- Production reliability

---

# 🏆 Project Positioning

### Short Description

> **DineVoice is a production-grade AI voice agent that enables customers to order food directly from restaurants using natural voice conversations. It combines real-time streaming voice AI, LangGraph agent workflows, RAG, tool calling, restaurant ordering APIs, and production-focused latency, evaluation, and scalability engineering.**

### Resume-Friendly Version

> Built a production-oriented real-time AI voice ordering agent using LiveKit, Python, LangGraph, RAG, Qdrant, streaming STT/TTS, structured tool calling, PostgreSQL, and AWS, enabling customers to discover menu items, customize food, manage carts, and place orders through natural voice conversations.

---

# 📌 Project Status

This project is being developed incrementally.

Architecture, benchmark tables, performance numbers, and production metrics will be updated as they are actually implemented and measured.

**No benchmark or scalability number should be claimed unless it has been experimentally verified.**
