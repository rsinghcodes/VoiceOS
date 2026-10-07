# VoiceOS — Brain

> **Architecture and engineering source of truth for the VoiceOS platform.**

VoiceOS is a **production-grade, configurable AI voice agent platform** designed to let businesses interact with customers through natural voice conversations.

The platform separates the **generic AI/voice infrastructure** from **business-specific capabilities and integrations**.

The first implementation is a **restaurant food-ordering agent**, but the core architecture is intentionally designed to support other business workflows such as:

- Restaurant food ordering
- Salon appointment booking
- Hotel services
- E-commerce ordering
- Service-business bookings
- Customer support workflows

The objective is not to build multiple unrelated voice bots.

The objective is to build **one reusable AI voice-agent platform with configurable business capabilities.**

---

# 1. Product Vision

## The Problem

Businesses receive repetitive phone calls for tasks such as:

- Product/service questions
- Availability checks
- Orders
- Bookings
- Cancellations
- Modifications
- Status queries
- FAQs
- Customer support

Traditional IVR systems rely heavily on:

```text
Press 1 for Orders
Press 2 for Support
Press 3 for Delivery
```

They are rigid and difficult to maintain.

VoiceOS replaces this with a conversational interface:

```text
Customer
   │
   │ Natural speech
   ▼
AI Voice Agent
   │
   ├── Understand intent
   ├── Retrieve information
   ├── Ask clarification
   ├── Execute business operations
   └── Confirm result
```

---

# 2. Core Architectural Principle

The most important design decision is:

> **The AI agent should not contain business-specific logic.**

The agent should understand generic concepts such as:

```text
Catalog
Product
Service
Availability
Cart
Order
Booking
Customer
Payment
Fulfillment
Status
```

Business-specific behavior is provided through:

```text
Business Configuration
+
Capabilities
+
Business Adapters
+
Business Knowledge
```

Therefore:

```text
VoiceOS Core
     │
     ├── Restaurant configuration
     ├── Salon configuration
     ├── Hotel configuration
     └── E-commerce configuration
```

The core voice and agent infrastructure remains reusable.

---

# 3. Architecture Goals

The system is designed around the following goals.

## G1 — Business Agnostic

The core should not contain restaurant-specific assumptions.

Bad:

```python
create_pizza_order()
```

Better:

```python
create_order()
```

Bad:

```python
check_table_availability()
```

Better:

```python
check_availability()
```

The business adapter determines what the operation actually means.

---

## G2 — Configuration Driven

Business behavior should be controlled by configuration wherever possible.

Example:

```yaml
business:
  id: restaurant_001
  type: restaurant
  name: 'ABC Restaurant'

capabilities:
  - catalog
  - ordering
  - delivery
  - order_tracking
  - cancellation
```

Another business:

```yaml
business:
  id: salon_001
  type: salon
  name: 'ABC Salon'

capabilities:
  - services
  - appointment_booking
  - appointment_rescheduling
  - appointment_cancellation
```

The same agent platform can serve both.

---

## G3 — LLM Does Not Own Business State

The LLM is responsible for:

- Understanding language
- Reasoning about intent
- Selecting tools
- Producing natural responses

The application is responsible for:

- Cart state
- Prices
- Availability
- Orders
- Payments
- Authentication
- Business rules
- Transaction integrity

This separation is critical.

```text
             LLM
              │
              │ decides what it wants to do
              ▼
        Tool Invocation
              │
              ▼
       Application Logic
              │
              │ validates
              ▼
         Business API
              │
              ▼
           Database
```

---

# 4. High-Level Architecture

```text
                         CUSTOMER
                            │
                            │ Voice
                            ▼
                  ┌─────────────────────┐
                  │       LiveKit       │
                  │   WebRTC / Audio    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Voice Pipeline    │
                  │                     │
                  │ VAD → STT → TTS     │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Conversation Layer │
                  │                     │
                  │ Session Management  │
                  │ Turn Management     │
                  │ Interruption        │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Agent Engine     │
                  │      LangGraph      │
                  │                     │
                  │ State / Routing     │
                  │ Reasoning / Tools   │
                  └──────────┬──────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
             RAG         Tool Layer    Memory
                │            │            │
                │            ▼            │
                │      Capability Layer   │
                │            │            │
                │            ▼            │
                │    Business Adapter    │
                │            │            │
                └────────────┼────────────┘
                             │
                             ▼
                    Business Systems
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
      PostgreSQL          External APIs       Redis
          │
          ▼
       Qdrant
```

---

# 5. Technology Stack

## Primary Stack

| Layer             | Technology               | Why                                                        |
| ----------------- | ------------------------ | ---------------------------------------------------------- |
| Language          | Python                   | Strong AI/ML ecosystem and excellent async/backend support |
| Voice transport   | LiveKit                  | Real-time audio infrastructure and WebRTC support          |
| Protocol          | WebRTC                   | Low-latency real-time communication                        |
| STT               | Streaming STT provider   | Converts speech to text with low latency                   |
| TTS               | Streaming TTS provider   | Produces natural streaming speech                          |
| Agent             | LangGraph                | Stateful, controllable agent workflows                     |
| LLM               | API + open-source models | Allows quality/cost/latency comparison                     |
| Backend           | FastAPI                  | High-performance async Python API framework                |
| Validation        | Pydantic                 | Strong typed validation and structured data                |
| RAG               | Qdrant                   | Vector search with metadata filtering                      |
| Database          | PostgreSQL               | Reliable transactional business data                       |
| Cache             | Redis                    | Fast session/cache/state-support layer                     |
| ORM               | SQLAlchemy               | Mature Python database abstraction                         |
| Migrations        | Alembic                  | Reliable PostgreSQL schema migrations                      |
| Containers        | Docker                   | Reproducible deployment                                    |
| Cloud             | AWS                      | Production deployment and infrastructure experience        |
| Testing           | Pytest                   | Python testing standard                                    |
| Load testing      | Locust                   | Realistic concurrent-load testing                          |
| Observability     | OpenTelemetry            | Distributed tracing and telemetry                          |
| Monitoring        | CloudWatch               | AWS-native monitoring                                      |
| Model serving     | vLLM                     | High-throughput LLM inference experiments                  |
| Model development | Hugging Face + PyTorch   | Open-source model experimentation and fine-tuning          |

---

# 6. Why Python?

Python is the primary language.

It is used because VoiceOS combines:

```text
AI
+
LLMs
+
RAG
+
Voice
+
Backend APIs
+
Evaluation
+
Model inference
```

Python provides mature libraries for all of these areas.

It also allows the same language to be used across:

- Agent logic
- RAG
- Evaluation
- Backend
- Model experimentation
- Data processing
- Testing

This reduces unnecessary technology fragmentation.

---

# 7. Why FastAPI?

FastAPI is the primary backend framework.

Responsibilities include:

```text
REST APIs
Authentication
Business APIs
Webhook handling
Health checks
Admin APIs
Order APIs
Evaluation APIs
```

Why FastAPI?

### Async-first

Voice applications involve many I/O operations:

```text
STT
LLM
TTS
Database
Vector DB
External APIs
```

Async execution is important for handling concurrent sessions efficiently.

### Type safety

FastAPI integrates naturally with Pydantic.

Example:

```python
class CreateOrderRequest(BaseModel):
    customer_id: str
    items: list[OrderItem]
```

### API documentation

FastAPI automatically generates OpenAPI documentation.

This is useful when connecting external business systems.

---

# 8. Why LiveKit?

LiveKit is the real-time communication layer.

Responsibilities:

- Audio transport
- WebRTC
- Voice sessions
- Participant management
- Streaming audio
- Real-time communication

We don't want to build WebRTC infrastructure ourselves.

LiveKit allows the project to focus on:

```text
AI
Agent behavior
Latency
Reliability
Business workflows
```

instead of implementing low-level real-time communication infrastructure.

---

# 9. Why WebRTC?

Voice interaction requires low-latency bidirectional communication.

WebRTC provides:

- Real-time media transport
- Low latency
- Audio streaming
- Browser/device compatibility

The architecture treats the voice channel independently from the agent.

Therefore the same agent engine could potentially receive input from:

```text
Phone
WebRTC
Web application
Future voice channels
```

without changing the business logic.

---

# 10. Voice Pipeline

The voice pipeline is:

```text
Audio Input
     │
     ▼
    VAD
     │
     ▼
Streaming STT
     │
     ▼
Transcript
     │
     ▼
Agent
     │
     ▼
Streaming TTS
     │
     ▼
Audio Output
```

---

# 11. Voice Activity Detection

VAD determines:

```text
When the customer starts speaking
When the customer stops speaking
```

This prevents unnecessary processing of silence.

It is important for:

- Latency
- Cost
- Turn detection
- Interruption handling

---

# 12. Streaming STT

Speech-to-text should operate in streaming mode where supported.

Instead of:

```text
Wait for complete sentence
        ↓
Send to STT
        ↓
Receive transcript
```

we aim for:

```text
Speech
 ↓
Partial transcript
 ↓
Updated transcript
 ↓
Final transcript
```

This reduces perceived latency.

---

# 13. Streaming TTS

The response should also be streamed.

Instead of:

```text
Generate entire response
       ↓
Generate entire audio
       ↓
Play audio
```

use:

```text
LLM tokens
     ↓
TTS chunks
     ↓
Audio chunks
     ↓
Customer
```

This allows the agent to start speaking sooner.

---

# 14. Barge-In / Interruption Handling

Natural conversations require interruption support.

Example:

```text
AI:
"Your total is ₹650 and your estimated delivery—"

Customer:
"Wait, remove the Coke."

AI stops speaking.
```

The system should:

1. Detect customer speech
2. Stop current TTS playback
3. Preserve relevant conversation state
4. Process the new request
5. Continue the conversation

This is a major requirement for natural voice interaction.

---

# 15. Why LangGraph?

LangGraph is the agent orchestration framework.

It is preferred because the application requires:

- Explicit state
- Multi-step workflows
- Conditional routing
- Tool execution
- Retry handling
- Human handoff
- Long-running workflows
- Checkpointing/state persistence

A generic chain is insufficient for these workflows.

Example:

```text
START
  │
  ▼
Understand Intent
  │
  ├── Question ──────────► RAG
  │
  ├── Order ─────────────► Catalog
  │
  ├── Existing Order ────► Order Status
  │
  └── Human Request ─────► Human Handoff
```

---

# 16. Agent State

LangGraph maintains application-level agent state.

Example:

```python
class AgentState(TypedDict):
    session_id: str
    business_id: str
    customer_id: str
    messages: list
    intent: str | None
    cart_id: str | None
    order_id: str | None
    tool_results: list
    confidence: float | None
```

State should contain only information required by the workflow.

Large conversation histories should not be blindly passed to the LLM.

---

# 17. Why Pydantic?

Pydantic is used for:

- Request validation
- Tool arguments
- LLM structured outputs
- Configuration
- API schemas
- Internal data contracts

Example:

```python
class AddToCart(BaseModel):
    product_id: str
    quantity: int
    customizations: list[str] = []
```

This prevents malformed tool calls from reaching business systems.

---

# 18. Tool Architecture

Tools are the controlled interface between the AI and the application.

Generic tools may include:

```text
search_catalog()
get_product()
check_availability()

create_cart()
get_cart()
add_to_cart()
update_cart()
remove_from_cart()

calculate_total()

create_order()
get_order_status()
cancel_order()

search_knowledge()
transfer_to_human()
```

The exact tools exposed depend on the business capabilities.

---

# 19. Capability System

Businesses declare capabilities.

Example:

```yaml
capabilities:
  - catalog
  - cart
  - ordering
  - delivery
  - order_tracking
```

A salon might use:

```yaml
capabilities:
  - services
  - availability
  - appointment_booking
  - appointment_rescheduling
  - appointment_cancellation
```

The agent should only have access to tools supported by the current business.

This reduces:

- Tool confusion
- Invalid actions
- Prompt complexity
- Unnecessary tool calls

---

# 20. Business Adapter Layer

The adapter pattern isolates external business systems from the agent.

Interface:

```python
class BusinessAdapter(Protocol):

    async def search_catalog(self, query: str):
        ...

    async def get_product(self, product_id: str):
        ...

    async def check_availability(self, product_id: str):
        ...

    async def create_transaction(self, data):
        ...

    async def get_status(self, transaction_id: str):
        ...
```

A restaurant implementation may connect to:

```text
Restaurant POS
Restaurant API
PostgreSQL
```

A future e-commerce implementation could connect to:

```text
Shopify
Custom Commerce API
```

The agent does not need to know the difference.

---

# 21. Why Adapter Pattern?

The Adapter pattern is intentionally used here.

Without adapters:

```text
Agent
 ├── Restaurant logic
 ├── Salon logic
 ├── Hotel logic
 └── E-commerce logic
```

This becomes tightly coupled.

With adapters:

```text
Agent
  │
  ▼
Business Interface
  │
  ├── RestaurantAdapter
  ├── SalonAdapter
  ├── HotelAdapter
  └── EcommerceAdapter
```

The core agent remains stable.

---

# 22. Restaurant Reference Implementation

The first business implementation is restaurant food ordering.

Capabilities:

```text
catalog
menu_search
availability
cart
customization
ordering
delivery
pickup
order_tracking
cancellation
```

Example workflow:

```text
Customer
   │
   ▼
"What burgers do you have?"
   │
   ▼
Catalog Search
   │
   ▼
"Add two chicken burgers."
   │
   ▼
Availability Check
   │
   ▼
Cart
   │
   ▼
Customization
   │
   ▼
Total Calculation
   │
   ▼
Customer Confirmation
   │
   ▼
Create Order
```

Restaurant-specific behavior lives inside the restaurant adapter/configuration.

---

# 23. Why PostgreSQL?

PostgreSQL stores authoritative transactional data.

Examples:

```text
Businesses
Customers
Products
Categories
Orders
Order Items
Transactions
Payments
Events
```

PostgreSQL is preferred because ordering workflows require:

- ACID transactions
- Relationships
- Constraints
- Indexing
- Reliable updates
- Strong consistency

An LLM must never be the source of truth for transactional information.

---

# 24. Why SQLAlchemy?

SQLAlchemy provides:

- Database abstraction
- ORM support
- Query construction
- Transactions
- Connection pooling

It also keeps business logic independent from raw SQL where appropriate.

---

# 25. Why Alembic?

Alembic manages database schema migrations.

Example:

```text
Migration 001
Create businesses

Migration 002
Create products

Migration 003
Create orders

Migration 004
Add order events
```

Production systems should not depend on manually modifying database schemas.

---

# 26. Why Redis?

Redis is used for fast, temporary data.

Potential use cases:

```text
Session state
Conversation metadata
Caching
Rate limiting
Distributed locks
Short-lived workflow state
```

Redis is not the authoritative order database.

PostgreSQL remains the source of truth.

---

# 27. Why Qdrant?

Qdrant is used for semantic retrieval.

Good candidates for vector search:

```text
FAQs
Policies
Product descriptions
Business information
Unstructured documentation
Dietary information
Customer-support knowledge
```

Structured transactional data should remain in PostgreSQL.

Therefore:

```text
Structured facts → PostgreSQL
Semantic knowledge → Qdrant
```

---

# 28. RAG Architecture

```text
Documents
    │
    ▼
Parsing
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
Qdrant
    │
    ▼
Metadata Filtering
    │
    ▼
Top-K Retrieval
    │
    ▼
Reranking
    │
    ▼
Context Selection
    │
    ▼
LLM
```

---

# 29. RAG Metadata

Every document should contain business identity.

Example:

```json
{
  "business_id": "restaurant_001",
  "document_type": "menu",
  "category": "burgers",
  "product_id": "burger_123"
}
```

This prevents information from one business being retrieved for another.

Multi-tenant isolation is a fundamental requirement.

---

# 30. Structured Data vs RAG

The system should not use RAG for everything.

### Use PostgreSQL/API for:

```text
Current price
Inventory
Availability
Order status
Customer data
Cart
Order creation
```

### Use RAG for:

```text
FAQs
Policies
Descriptions
Business information
Unstructured documents
```

This distinction improves correctness.

---

# 31. LLM Responsibilities

The LLM is responsible for:

```text
Intent understanding
Natural language interpretation
Clarification
Tool selection
Response generation
Conversation reasoning
```

The LLM is NOT responsible for:

```text
Pricing
Inventory truth
Order persistence
Payment authorization
Database integrity
Business authorization
```

---

# 32. Deterministic Business Logic

Critical calculations should be deterministic.

Example:

```text
Cart
 │
 ▼
Backend
 │
 ├── Item price
 ├── Quantity
 ├── Discounts
 ├── Tax
 └── Delivery fee
 │
 ▼
Final Total
```

Never ask the LLM:

> "Calculate the final order price."

Instead:

```python
calculate_order_total(cart_id)
```

The backend returns the authoritative result.

---

# 33. Order Safety

Order creation requires explicit confirmation.

Preferred flow:

```text
Customer Request
      │
      ▼
Build Cart
      │
      ▼
Calculate Total
      │
      ▼
Read Back Order
      │
      ▼
Explicit Confirmation
      │
      ▼
Create Order
```

The system should prevent accidental order creation from ambiguous language.

---

# 34. Idempotency

Order creation must be idempotent.

If a network failure occurs:

```text
AI → create_order()
       │
       ▼
Backend creates order
       │
       X
Response lost
```

The agent may retry.

Without idempotency:

```text
Two orders
```

With idempotency:

```text
Same idempotency key
        ↓
Existing order returned
```

This is essential for production reliability.

---

# 35. Error Handling

Errors should be classified.

```text
Transient
    ↓
Retry

Validation
    ↓
Ask user / correct input

Business
    ↓
Explain constraint

System
    ↓
Fallback / human handoff
```

Example:

```text
Payment service unavailable
        ↓
Do not create duplicate order
        ↓
Inform customer
        ↓
Offer supported fallback
```

---

# 36. Human Handoff

Human handoff is part of the architecture, not an afterthought.

Triggers:

```text
Explicit customer request
Low confidence
Repeated misunderstanding
Unsupported workflow
Payment issue
Complex complaint
Business-defined escalation
```

The human should receive:

```text
Customer
Current conversation summary
Current cart/order
Detected intent
Failure reason
Relevant tool results
```

---

# 37. Authentication & Authorization

The backend must distinguish:

```text
Customer
Business Admin
System Agent
Internal Services
```

Business APIs should be scoped to the correct:

```text
business_id
customer_id
session_id
```

The AI agent should never be allowed to arbitrarily access another business's data.

---

# 38. Multi-Tenant Architecture

VoiceOS is conceptually multi-tenant.

Every business-owned resource should be associated with:

```text
business_id
```

Example:

```text
business_id
    │
    ├── configuration
    ├── capabilities
    ├── knowledge base
    ├── catalog
    ├── customers
    └── orders
```

This allows the same platform to serve multiple businesses.

---

# 39. Configuration Architecture

Example:

```text
config/
├── platform.yaml
├── businesses/
│   ├── restaurant_001.yaml
│   ├── salon_001.yaml
│   └── hotel_001.yaml
└── prompts/
    ├── base.yaml
    └── business/
```

Business configuration may contain:

```yaml
business:
  id: restaurant_001
  type: restaurant
  name: ABC Restaurant

voice:
  language: en-IN
  tone: friendly

capabilities:
  - catalog
  - ordering
  - delivery
  - pickup
  - tracking

policies:
  require_order_confirmation: true
  allow_cancellation: true
```

---

# 40. Prompt Architecture

Prompts should be layered.

```text
Base System Prompt
        │
        ▼
Platform Rules
        │
        ▼
Business Context
        │
        ▼
Capability Instructions
        │
        ▼
Current Workflow
```

The core system prompt should not contain restaurant-specific instructions.

---

# 41. Why Not Hardcode Prompts Per Business?

Hardcoding:

```text
You are a restaurant ordering assistant...
```

makes reuse difficult.

Instead:

```text
You are the voice assistant for {{business.name}}.

Your available capabilities are:
{{capabilities}}

Follow these business rules:
{{policies}}
```

This allows business configuration to influence behavior without rewriting the agent.

---

# 42. Model Strategy

The architecture should not be tied permanently to one LLM provider.

Create an abstraction:

```text
LLM Interface
     │
     ├── OpenAI
     ├── Gemini
     ├── Anthropic
     └── Open-source
```

This allows benchmarking.

Compare:

```text
Accuracy
Tool-calling reliability
TTFT
Latency
Cost
Context handling
```

---

# 43. Why API + Open-Source Models?

API models provide:

- Strong quality
- Easy deployment
- Fast experimentation

Open-source models provide:

- Deployment control
- Cost optimization opportunities
- Fine-tuning
- Quantization
- GPU inference experience

Using both makes the project more valuable as an AI engineering portfolio.

---

# 44. Model Serving — vLLM

vLLM is used for experimentation with self-hosted LLM inference.

Potential architecture:

```text
FastAPI
   │
   ▼
Agent
   │
   ▼
LLM Interface
   │
   ▼
vLLM
   │
   ▼
GPU
```

Areas to benchmark:

- Throughput
- TTFT
- Concurrent requests
- GPU memory
- Token generation speed

We should use existing optimized implementations rather than attempting to implement low-level GPU kernels ourselves.

---

# 45. Quantization

For self-hosted models, evaluate:

```text
FP16
BF16
INT8
INT4
```

Compare:

```text
Quality
Latency
GPU memory
Throughput
Cost
```

The objective is to understand the trade-off between model quality and infrastructure efficiency.

---

# 46. Fine-Tuning

Fine-tuning is optional for the initial platform.

If implemented, focus on a narrowly defined task such as:

```text
Intent classification
Structured order extraction
Tool selection
```

Potential stack:

```text
PyTorch
Hugging Face Transformers
PEFT
LoRA
QLoRA
```

Fine-tuning should only be introduced when evaluation demonstrates that prompting or model selection is insufficient.

---

# 47. Evaluation Architecture

Evaluation is a first-class component.

```text
Test Dataset
     │
     ▼
Agent
     │
     ▼
Trace
     │
     ▼
Evaluators
     │
 ┌───┼───────────────┐
 ▼   ▼               ▼
RAG Tool           Workflow
Eval Eval          Eval
 │   │               │
 └───┼───────────────┘
     ▼
Evaluation Report
```

---

# 48. Evaluation Categories

## Voice

- STT accuracy
- Turn detection
- Interruption handling
- Time to first audio
- End-to-end latency

## Agent

- Intent accuracy
- Tool selection accuracy
- Tool argument accuracy
- Workflow completion
- Recovery behavior

## RAG

- Recall@K
- Precision@K
- MRR
- Context relevance
- Groundedness

## Transactional

- Cart correctness
- Price correctness
- Order correctness
- Duplicate order rate

---

# 49. Golden Dataset

Create a deterministic evaluation dataset.

Example:

```json
{
  "input": "I want two chicken burgers without onions",
  "expected_intent": "add_to_cart",
  "expected_tool": "add_to_cart",
  "expected_arguments": {
    "quantity": 2,
    "customizations": ["no onions"]
  }
}
```

The dataset should include:

- Normal requests
- Ambiguous requests
- Corrections
- Interruptions
- Invalid requests
- Multi-turn conversations
- Edge cases

---

# 50. Observability

Every conversation should produce a trace.

Example:

```text
Trace ID
 │
 ├── STT latency
 │
 ├── Intent detection
 │
 ├── Retrieval
 │
 ├── LLM request
 │
 ├── Tool call
 │
 ├── Database query
 │
 ├── TTS latency
 │
 └── Final response
```

---

# 51. OpenTelemetry

OpenTelemetry provides standardized telemetry.

Use it for:

- Traces
- Metrics
- Correlation IDs
- Service-level visibility

A single voice request should be traceable across:

```text
LiveKit
 → API
 → Agent
 → RAG
 → PostgreSQL
 → External API
 → TTS
```

---

# 52. AWS

AWS is the target production cloud.

Initial deployment may use:

```text
AWS
 │
 ├── ECS / EC2
 ├── Application Load Balancer
 ├── RDS PostgreSQL
 ├── ElastiCache Redis
 ├── S3
 ├── CloudWatch
 └── IAM
```

The exact deployment topology may evolve based on load-testing results.

---

# 53. Why Docker?

Every service should be reproducible.

Docker provides:

```text
Development consistency
Testing consistency
Production consistency
Isolation
Easy deployment
```

Example:

```text
API container
Worker container
Evaluation container
PostgreSQL
Redis
Qdrant
```

---

# 54. Load Testing

Locust will simulate concurrent users.

Test progression:

```text
1
10
50
100
500
...
```

Measure:

```text
P50
P95
P99

Error rate
Throughput
CPU
Memory
GPU
Database latency
```

We will never publish estimated numbers as actual benchmark results.

---

# 55. Performance Budget

Latency should be treated as a measurable engineering constraint.

```text
User stops speaking
        │
        ▼
STT
        │
        ▼
Agent
        │
        ▼
Tool / RAG
        │
        ▼
LLM
        │
        ▼
TTS
        │
        ▼
First audio
```

Each stage gets independently measured.

This allows us to identify the real bottleneck instead of optimizing blindly.

---

# 56. Caching Strategy

Potential caching layers:

```text
Redis
 │
 ├── Frequently requested business information
 ├── Menu metadata
 ├── Configuration
 └── Short-lived session data
```

Do not cache data where stale information could cause incorrect transactions unless appropriate invalidation is implemented.

For example:

```text
Current inventory
Current price
Order status
```

should have stricter freshness requirements than:

```text
Restaurant description
FAQ
Opening-hour documentation
```

---

# 57. Reliability Principles

The platform follows these principles:

### Principle 1

**LLM output is untrusted input.**

Validate it.

### Principle 2

**Database is the source of truth.**

Not the LLM.

### Principle 3

**Critical actions require deterministic validation.**

### Principle 4

**Every external operation can fail.**

Handle retries and timeouts.

### Principle 5

**Retries must be safe.**

Use idempotency.

### Principle 6

**The customer should always have a recovery path.**

Human handoff is part of reliability.

---

# 58. Security Principles

The system should protect:

- Customer data
- Business data
- API credentials
- Payment information
- Authentication tokens
- Internal system details

Never expose:

```text
API keys
Database credentials
Internal prompts
System architecture secrets
Private customer information
```

through the voice response.

---

# 59. Secrets Management

Secrets should never be committed to Git.

Development:

```text
.env
```

Production:

```text
AWS Secrets Manager
```

Potential secrets:

```text
LLM API keys
LiveKit credentials
Database credentials
Redis credentials
External business API credentials
```

---

# 60. Project Structure

```text
voiceos/
│
├── app/
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── agent/
│   │   ├── graph/
│   │   ├── state/
│   │   ├── nodes/
│   │   ├── prompts/
│   │   └── tools/
│   │
│   ├── voice/
│   │   ├── livekit/
│   │   ├── stt/
│   │   ├── tts/
│   │   ├── vad/
│   │   └── interruption/
│   │
│   ├── capabilities/
│   │   ├── catalog/
│   │   ├── cart/
│   │   ├── ordering/
│   │   ├── booking/
│   │   ├── tracking/
│   │   └── cancellation/
│   │
│   ├── businesses/
│   │   ├── base/
│   │   ├── restaurant/
│   │   ├── salon/
│   │   └── adapters/
│   │
│   ├── rag/
│   │   ├── ingestion/
│   │   ├── chunking/
│   │   ├── embeddings/
│   │   ├── retrieval/
│   │   └── reranking/
│   │
│   ├── llm/
│   │   ├── interface.py
│   │   ├── providers/
│   │   └── routing/
│   │
│   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── migrations/
│   │
│   ├── services/
│   │   ├── orders/
│   │   ├── customers/
│   │   └── businesses/
│   │
│   ├── observability/
│   │   ├── logging/
│   │   ├── tracing/
│   │   └── metrics/
│   │
│   └── config/
│
├── evaluation/
│   ├── datasets/
│   ├── runners/
│   ├── evaluators/
│   └── reports/
│
├── benchmarks/
│   ├── latency/
│   ├── models/
│   ├── inference/
│   └── load/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── load/
│
├── businesses/
│   └── restaurant_001/
│       ├── config.yaml
│       └── knowledge/
│
├── infrastructure/
│   ├── docker/
│   └── aws/
│
├── scripts/
│
├── docs/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

# 61. Request Lifecycle

A complete voice interaction should follow this conceptual flow:

```text
Customer speaks
       │
       ▼
LiveKit
       │
       ▼
VAD
       │
       ▼
Streaming STT
       │
       ▼
Conversation Manager
       │
       ▼
LangGraph
       │
       ├──────────────┐
       │              │
       ▼              ▼
      RAG           Tools
       │              │
       │              ▼
       │        Capability Layer
       │              │
       │              ▼
       │        Business Adapter
       │              │
       │              ▼
       │        External System
       │
       └──────┬───────┘
              ▼
             LLM
              │
              ▼
          Response
              │
              ▼
          Streaming TTS
              │
              ▼
           LiveKit
              │
              ▼
          Customer
```

---

# 62. Example: Restaurant

Business configuration:

```yaml
business:
  type: restaurant

capabilities:
  - catalog
  - cart
  - ordering
  - delivery
  - pickup
  - tracking
  - cancellation
```

Customer:

> "I want two chicken burgers, one without onions."

Agent:

```text
Intent
  ↓
ADD_TO_CART
  ↓
search_catalog()
  ↓
get_product()
  ↓
check_availability()
  ↓
add_to_cart()
```

Then:

```text
calculate_total()
       ↓
read cart
       ↓
customer confirmation
       ↓
create_order()
```

---

# 63. Example: Salon

No core agent rewrite should be required.

Configuration:

```yaml
business:
  type: salon

capabilities:
  - services
  - availability
  - appointment_booking
  - appointment_rescheduling
  - cancellation
```

Conversation:

> "I'd like a haircut tomorrow afternoon."

Agent:

```text
Intent
  ↓
BOOK_APPOINTMENT
  ↓
search_services()
  ↓
check_availability()
  ↓
confirm_time()
  ↓
create_booking()
```

Same:

```text
Voice
STT
LangGraph
RAG
Observability
Evaluation
```

Different:

```text
Capabilities
Business Adapter
Knowledge
Configuration
```

This proves the architecture is genuinely reusable.

---

# 64. Example: E-commerce

Configuration:

```yaml
business:
  type: ecommerce

capabilities:
  - catalog
  - cart
  - ordering
  - shipping
  - order_tracking
  - cancellation
```

The same platform could handle:

> "Do you have the 32GB model?"

> "Add it to my cart."

> "What's the delivery time to Delhi?"

> "Place the order."

Again, only business-specific integrations change.

---

# 65. Design Patterns

The project intentionally uses several software engineering patterns.

## Adapter

Used for:

```text
Business integrations
External APIs
LLM providers
```

## Strategy

Used for:

```text
LLM selection
Retrieval strategies
STT/TTS providers
```

Example:

```text
LLMStrategy
 ├── OpenAI
 ├── Gemini
 └── LocalModel
```

## Factory

Used for:

```text
Creating business adapters
Creating model clients
Creating provider implementations
```

## State

Implemented naturally through:

```text
LangGraph
```

Used for:

```text
Conversation state
Order workflow
Agent execution
```

## Repository

Used to separate:

```text
Business logic
     ↓
Database access
```

These patterns should be used where they solve an actual architectural problem, not merely to demonstrate design patterns.

---

# 66. Why Not Microservices Initially?

The first implementation should be a **modular monolith**.

```text
One deployable application
        │
        ├── Agent
        ├── Voice
        ├── RAG
        ├── Business
        ├── Orders
        └── API
```

Why?

Because premature microservices introduce:

- Network complexity
- Deployment complexity
- Distributed debugging
- More infrastructure
- More operational overhead

The internal modules should have clean boundaries so that components can be extracted later if scale requires it.

---

# 67. Scaling Strategy

Initial:

```text
Modular Monolith
```

Then scale independently where necessary:

```text
Voice Workers
      │
      ▼
Agent Workers
      │
      ▼
API Servers
      │
      ▼
PostgreSQL / Redis / Qdrant
```

If model inference becomes the bottleneck:

```text
Application
    │
    ▼
Inference Service
    │
    ▼
GPU Cluster
```

Architecture should evolve based on measured bottlenecks.

---

# 68. Development Phases

## Phase 1 — Foundation

Build:

```text
Python
FastAPI
PostgreSQL
Docker
Pydantic
Configuration
```

---

## Phase 2 — Voice

Build:

```text
LiveKit
VAD
STT
TTS
Streaming
Barge-in
```

---

## Phase 3 — Agent

Build:

```text
LangGraph
State
Intent routing
Tools
Tool validation
Retries
```

---

## Phase 4 — Restaurant

Build:

```text
Menu
Catalog
Cart
Customization
Availability
Pricing
Ordering
Delivery/Pickup
Tracking
Cancellation
```

---

## Phase 5 — RAG

Build:

```text
Ingestion
Embeddings
Qdrant
Retrieval
Metadata filtering
Reranking
Evaluation
```

---

## Phase 6 — Production Engineering

Build:

```text
Redis
Caching
Observability
OpenTelemetry
AWS
Docker deployment
Load testing
```

---

## Phase 7 — Model Engineering

Experiment with:

```text
Hugging Face
Open-source LLMs
Quantization
LoRA
QLoRA
vLLM
```

Only after the core workflow works reliably.

---

## Phase 8 — Reusability Validation

Build a second business adapter.

For example:

```text
Restaurant
      ↓
Salon
```

The goal is to demonstrate:

```text
Same Core
Different Business
```

without duplicating the entire application.

---

# 69. Definition of Done

The project should not be considered complete merely because the voice agent can answer questions.

A production-oriented milestone requires:

### Voice

- [ ] Streaming audio
- [ ] Low-latency STT
- [ ] Low-latency TTS
- [ ] Barge-in
- [ ] Error recovery

### Agent

- [ ] LangGraph workflow
- [ ] Structured state
- [ ] Tool calling
- [ ] Validation
- [ ] Retry logic
- [ ] Human handoff

### Business

- [ ] Restaurant ordering
- [ ] Cart
- [ ] Customization
- [ ] Availability
- [ ] Pricing
- [ ] Order creation
- [ ] Order tracking

### RAG

- [ ] Ingestion
- [ ] Qdrant
- [ ] Retrieval
- [ ] Metadata filtering
- [ ] Reranking
- [ ] Evaluation

### Production

- [ ] Docker
- [ ] AWS
- [ ] PostgreSQL
- [ ] Redis
- [ ] Observability
- [ ] Load testing

### AI Engineering

- [ ] Model comparison
- [ ] Latency benchmarks
- [ ] Agent evaluation
- [ ] RAG evaluation
- [ ] Inference experiment
- [ ] Quantization experiment
- [ ] vLLM experiment

### Architecture

- [ ] Business configuration
- [ ] Capability system
- [ ] Business adapter
- [ ] Multi-tenant isolation
- [ ] Second business adapter

---

# 70. Engineering Principles

The following principles should guide implementation.

### 1. Don't over-engineer before measuring.

Build the simplest correct architecture first.

### 2. Don't use an LLM where deterministic code is better.

Pricing, validation, transactions, and authorization should remain deterministic.

### 3. Don't use RAG where structured data is better.

Current prices and inventory belong in databases/APIs.

### 4. Don't hardcode business-specific behavior into the agent.

Use configuration and adapters.

### 5. Don't claim performance numbers without benchmarks.

Every latency, concurrency, or cost number must come from an actual experiment.

### 6. Don't optimize before identifying the bottleneck.

Measure first.

### 7. Treat AI output as untrusted input.

Validate everything before executing critical actions.

### 8. Design for failure.

External services will fail.

### 9. Keep the first deployment simple.

Use a modular monolith before introducing unnecessary distributed complexity.

### 10. Build for reuse, but prove reuse.

Restaurant is the first implementation.

A second business adapter is the proof that the abstraction works.

---

# 71. Final Architecture Philosophy

VoiceOS is not fundamentally a restaurant bot.

It is:

```text
             VOICEOS
                │
        ┌───────┴────────┐
        │                │
   Generic Core     Business Layer
        │                │
        │          ┌─────┼─────┐
        │          │     │     │
        │     Restaurant Salon Hotel
        │
        ├── Voice
        ├── Agent
        ├── RAG
        ├── Tools
        ├── State
        ├── Evaluation
        ├── Observability
        └── Infrastructure
```

The first business proves the platform can execute a real transactional workflow.

The second business proves that the architecture is reusable.

The production benchmarks prove that the system is engineered rather than simply prototyped.

The evaluation system proves that the AI behavior is measurable.

The model/inference experiments demonstrate deeper AI engineering capability.

---

# 72. One-Line Architecture Summary

> **VoiceOS is a configurable, multi-tenant AI voice-agent platform that combines real-time voice streaming, stateful LangGraph agents, RAG, validated tool execution, business adapters, transactional backends, evaluation, observability, and production infrastructure — with restaurant food ordering as its first reference implementation.**

---

# 73. Current Technology Decision

The initial implementation uses:

```text
Python
FastAPI
LiveKit
WebRTC
Streaming STT
Streaming TTS
LangGraph
Pydantic
PostgreSQL
SQLAlchemy
Alembic
Redis
Qdrant
Docker
AWS
OpenTelemetry
CloudWatch
Pytest
Locust
Hugging Face
PyTorch
PEFT
LoRA / QLoRA
vLLM
```

Technology should be replaced only when a measured requirement justifies the change.

The architecture matters more than any individual vendor.

---

# 74. Final Mental Model

When implementing any feature, ask:

```text
Is this:

1. Core Voice Infrastructure?
2. Agent Capability?
3. Business Configuration?
4. Business Adapter?
5. RAG Knowledge?
6. Transactional Business Logic?
7. External Integration?
8. Evaluation?
9. Observability?
```

If the feature is clearly classified, it should be easier to decide where it belongs.

The ultimate goal is:

```text
                ONE CORE
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   RESTAURANT    SALON       HOTEL
       │           │           │
       ▼           ▼           ▼
   Ordering     Booking     Services
```

while keeping:

```text
Voice
Agent
RAG
Evaluation
Observability
Infrastructure
```

shared across all businesses.
