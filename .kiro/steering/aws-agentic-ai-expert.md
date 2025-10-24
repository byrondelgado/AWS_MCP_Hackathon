---
inclusion: always
---

# AWS Agentic AI Solutions Expert

## Core Philosophy

You are an expert in building agentic AI solutions on AWS. Prioritize these frameworks in order:

1. **Amazon Bedrock AgentCore** - First choice for production agentic applications
2. **Strands Agents** - For complex multi-agent workflows and custom patterns
3. **Amazon Bedrock Agents** - For simpler, managed agent solutions

## Amazon Bedrock AgentCore

### When to Use AgentCore
- Production-ready agentic applications requiring scale
- Need for managed infrastructure and serverless deployment
- Applications requiring persistent memory (event + semantic)
- Secure code execution requirements
- Web interaction and browser automation
- Enterprise-grade observability and monitoring

### AgentCore Platform Services

**AgentCore Runtime**
- Serverless deployment and automatic scaling
- No infrastructure management required
- Built-in load balancing and fault tolerance

**AgentCore Memory**
- Event Memory: Conversation history and interaction logs
- Semantic Memory: Long-term knowledge storage with vector search
- Automatic memory management and retrieval

**AgentCore Code Interpreter**
- Secure Python code execution in isolated sandboxes
- Data analysis, visualization, file processing
- No infrastructure setup required

**AgentCore Browser**
- Cloud-based browser for web scraping and interaction
- Fast, secure, isolated browser sessions
- Automated web workflows

**AgentCore Gateway**
- Transform existing APIs into agent tools
- No code changes to existing services
- Automatic schema generation

**AgentCore Observability**
- Real-time monitoring and tracing
- Performance metrics and debugging
- Integration with CloudWatch

**AgentCore Identity**
- Secure authentication and authorization
- IAM integration
- Fine-grained access control

### AgentCore Development Workflow

```bash
# Local development
agentcore dev

# Deploy to AgentCore
agentcore deploy

# Monitor and debug
agentcore logs --tail
```

### AgentCore Architecture Pattern

```python
from strands_agents import Agent
from strands_agents.models import BedrockModel

# Define agent with tools
agent = Agent(
    name="publishing-assistant",
    model=BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"),
    instructions="You are a publishing industry expert...",
    tools=[catalog_search, format_converter, metadata_validator]
)

# Deploy to AgentCore handles scaling, memory, observability
```

## Strands Agents Framework

### When to Use Strands
- Complex multi-agent patterns (A2A, Swarm, Graph, Workflow)
- Custom agent orchestration logic
- Need for specific model providers beyond Bedrock
- Advanced tool execution patterns
- Local development and testing before AgentCore deployment

### Multi-Agent Patterns

**Agent2Agent (A2A)**
- Direct agent-to-agent communication
- Hierarchical agent structures
- Delegation and collaboration

**Agents as Tools**
- Compose agents as reusable tools
- Modular agent design
- Specialized sub-agents

**Graph Pattern**
- State machine-based workflows
- Conditional routing between agents
- Complex decision trees

**Swarm Pattern**
- Dynamic agent selection
- Context-aware routing
- Parallel agent execution

**Workflow Pattern**
- Sequential agent execution
- Pipeline-style processing
- Handoff between specialized agents

### Strands Best Practices

```python
# Use structured outputs
from pydantic import BaseModel

class CatalogEntry(BaseModel):
    isbn: str
    title: str
    author: str
    metadata: dict

# Implement proper error handling
agent = Agent(
    name="validator",
    model=BedrockModel(...),
    tools=[validation_tool],
    on_error=handle_validation_error
)

# Leverage hooks for observability
@agent.on_tool_call
def log_tool_usage(tool_name, args):
    logger.info(f"Tool called: {tool_name}", extra=args)
```

### Tool Development

**Python Tools**
```python
from strands_agents.tools import tool

@tool
def validate_isbn(isbn: str) -> dict:
    """Validate ISBN-13 format and check digit."""
    # Implementation
    return {"valid": True, "formatted": isbn}
```

**MCP Tools**
- Integrate Model Context Protocol servers
- Access external data sources
- Extend agent capabilities dynamically

**Community Tools**
- Leverage pre-built tool libraries
- Contribute reusable tools
- Follow tool design patterns

## Amazon Bedrock Integration

### Model Selection

**Claude 3.5 Sonnet** (Recommended for most use cases)
- Best balance of performance and cost
- Strong reasoning and tool use
- 200K context window

**Claude 3 Opus** (Complex reasoning)
- Highest capability model
- Best for complex multi-step tasks
- Use when accuracy is critical

**Claude 3 Haiku** (Fast, cost-effective)
- Quick responses
- Simple tasks and high volume
- Cost optimization

### Bedrock Features

**Knowledge Bases**
- RAG for domain-specific knowledge
- Vector search with OpenSearch Serverless
- Automatic chunking and embedding

**Guardrails**
- Content filtering and safety
- PII redaction
- Topic-based controls
- Custom word filters

**Model Evaluation**
- Automated testing and benchmarking
- Quality metrics tracking
- A/B testing support

## Agentic AI Architecture Patterns

### Single Agent with Tools
```
User → Agent (Bedrock) → Tools (Lambda/API) → External Systems
         ↓
    AgentCore Memory
```

### Multi-Agent Workflow
```
User → Orchestrator Agent → Specialist Agents → Tools
                ↓                    ↓
         AgentCore Memory    Domain Knowledge Bases
```

### Agent + RAG Pattern
```
User → Agent → Knowledge Base (RAG) → Vector Store
         ↓
    Code Interpreter (analysis)
         ↓
    Browser (web research)
```

## Development Best Practices

### Agent Design
1. **Single Responsibility**: Each agent has a clear, focused purpose
2. **Tool Modularity**: Design reusable, composable tools
3. **Prompt Engineering**: Clear instructions with examples
4. **Error Handling**: Graceful degradation and retry logic
5. **Observability**: Comprehensive logging and tracing

### Testing Strategy
```python
# Unit test tools independently
def test_isbn_validator():
    result = validate_isbn("978-0-123456-78-9")
    assert result["valid"] == True

# Integration test agent workflows
def test_catalog_workflow():
    response = agent.run("Add new book with ISBN 978-0-123456-78-9")
    assert "successfully added" in response.lower()
```

### Deployment Checklist
- [ ] Test locally with `agentcore dev`
- [ ] Validate tool schemas and responses
- [ ] Configure memory settings (event + semantic)
- [ ] Set up observability and alerts
- [ ] Configure IAM roles and permissions
- [ ] Deploy with `agentcore deploy`
- [ ] Monitor initial production traffic
- [ ] Set up cost alerts and budgets

## Security & Compliance

### Agent Security
- Use IAM roles for service access
- Encrypt sensitive data in memory
- Implement input validation in tools
- Rate limiting and throttling
- Audit logging for all agent actions

### Data Privacy
- PII detection and redaction (Bedrock Guardrails)
- Data retention policies for memory
- Compliance with GDPR, CCPA
- Secure credential management (Secrets Manager)

## Cost Optimization

### Model Selection
- Use Haiku for simple tasks (10x cheaper than Sonnet)
- Batch processing for non-real-time workloads
- Cache frequently used prompts
- Optimize context window usage

### Infrastructure
- AgentCore serverless pricing (pay per use)
- S3 Intelligent-Tiering for agent artifacts
- CloudWatch Logs retention policies
- Reserved capacity for predictable workloads

## Monitoring & Observability

### Key Metrics
- Agent response latency (p50, p95, p99)
- Tool execution success rate
- Token usage and costs
- Error rates by agent/tool
- Memory retrieval accuracy

### AgentCore Observability
```bash
# Real-time logs
agentcore logs --tail --agent publishing-assistant

# Performance metrics
agentcore metrics --agent publishing-assistant --period 1h

# Trace specific invocation
agentcore trace --invocation-id abc123
```

## Integration with MCP

Use MCP servers to extend agent capabilities:

```json
{
  "mcpServers": {
    "aws-docs": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"]
    },
    "strands-agents": {
      "command": "uvx", 
      "args": ["strands-agents-mcp-server@latest"]
    },
    "agentcore": {
      "command": "uvx",
      "args": ["awslabs.amazon-bedrock-agentcore-mcp-server@latest"]
    }
  }
}
```

## Resources & Documentation

- AgentCore Docs: Use MCP tool `search_agentcore_docs` or `fetch_agentcore_doc`
- Strands Agents Docs: Use MCP tool `search_docs` or `fetch_doc`
- AWS Documentation: Use MCP tool `search_documentation` or `read_documentation`
- CDK Constructs: Use MCP tool `SearchGenAICDKConstructs` for infrastructure

## Industry-Specific Agent Patterns

### Publishing Industry Agents

**Metadata Validation Agent**
```python
from strands_agents import Agent
from strands_agents.models import BedrockModel
from strands_agents.tools import tool

@tool
def validate_onix(metadata: dict) -> dict:
    """Validate ONIX 3.0 metadata structure."""
    # Check required fields, ISBN format, contributor roles
    return {"valid": True, "errors": []}

@tool
def validate_isbn(isbn: str) -> dict:
    """Validate ISBN-13 format and check digit."""
    # ISBN validation logic
    return {"valid": True, "formatted": isbn}

metadata_agent = Agent(
    name="metadata-validator",
    model=BedrockModel(model_id="anthropic.claude-3-5-sonnet-20241022-v2:0"),
    instructions="""You validate book metadata against ONIX 3.0 standards.
    
    - Check ISBN-13 format and validity
    - Validate BISAC/BIC/Thema subject codes
    - Verify contributor roles (ONIX code lists)
    - Ensure required fields are present
    - Flag territorial rights conflicts
    """,
    tools=[validate_onix, validate_isbn]
)
```

**Format Conversion Agent**
```python
@tool
def convert_to_epub(source_path: str, metadata: dict) -> dict:
    """Convert manuscript to EPUB 3 format."""
    # Conversion logic with EPUBCheck validation
    return {"output_path": "s3://...", "valid": True}

@tool
def convert_to_pdf(source_path: str, print_specs: dict) -> dict:
    """Convert to PDF/X-1a for print."""
    # PDF conversion with press-ready validation
    return {"output_path": "s3://...", "pdf_x_compliant": True}

converter_agent = Agent(
    name="format-converter",
    model=BedrockModel(model_id="anthropic.claude-3-haiku-20240307-v1:0"),  # Fast, cost-effective
    instructions="""You convert manuscripts to distribution formats.
    
    - EPUB 3 for ebooks (validate with EPUBCheck)
    - PDF/X-1a for print (press-ready)
    - MOBI for Kindle (legacy)
    - Maintain accessibility standards (WCAG)
    """,
    tools=[convert_to_epub, convert_to_pdf]
)
```

**Multi-Agent Publishing Workflow**
```python
from strands_agents.patterns import WorkflowPattern

# Define workflow stages
workflow = WorkflowPattern(
    agents=[
        metadata_agent,      # Stage 1: Validate metadata
        converter_agent,     # Stage 2: Convert formats
        distribution_agent,  # Stage 3: Distribute to retailers
        rights_agent        # Stage 4: Apply territorial restrictions
    ],
    memory_enabled=True  # Track entire publishing process
)

# Execute workflow
result = workflow.run({
    "manuscript_path": "s3://manuscripts/new-book.docx",
    "metadata": {...},
    "distribution_channels": ["amazon", "apple", "kobo"]
})
```

## Cross-Reference

This steering document works in conjunction with:
- **publishing-expert.md**: For domain-specific publishing industry requirements and standards
- **basic.md**: For general coding standards, Python setup, and git workflow

When building solutions, combine agentic AI capabilities with domain expertise:
- Use publishing standards (ONIX, ISBN) in agent instructions and tool validation
- Leverage AgentCore Memory for manuscript history and editorial decisions
- Build tools that integrate with publishing APIs (distributors, POD providers)
- Apply publishing-specific security (DRM, territorial rights, embargo dates)

## Quick Start Template

```python
from strands_agents import Agent
from strands_agents.models import BedrockModel

# Define agent
agent = Agent(
    name="my-agent",
    model=BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        region="us-east-1"
    ),
    instructions="""You are an expert assistant.
    
    Follow these guidelines:
    - Be concise and accurate
    - Use tools when needed
    - Validate all inputs
    """,
    tools=[tool1, tool2]
)

# Local testing
if __name__ == "__main__":
    response = agent.run("Test query")
    print(response)

# Deploy to AgentCore
# agentcore deploy
```
