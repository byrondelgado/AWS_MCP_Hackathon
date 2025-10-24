# Deadline Cloud Project

AWS Deadline Cloud project for cloud-based rendering and job scheduling using the Open Job Description (OpenJD) specification.

## Overview

This project provides tools and resources for working with AWS Deadline Cloud, a fully-managed service for scalable processing farms, job scheduling, and render management.

## Project Structure

```
.
├── .kiro/              # Kiro IDE configuration and steering rules
│   └── steering/       # AI assistant guidance documents
├── reference/          # Reference documentation
│   └── openjd-specifications/  # OpenJD specification and samples
└── README.md
```

## Prerequisites

- AWS Account with Deadline Cloud access
- AWS CLI configured
- Python 3.13+ (for Python-based workflows)
- Deadline Cloud CLI

## Key Concepts

### Architecture

- **Farm**: Container for project resources, budgets, and permissions
- **Queue**: Where jobs are submitted and scheduled (priority 1-100)
- **Fleet**: Group of worker nodes that execute tasks
- **Job**: Rendering request defined by OpenJD template
- **Session**: Ephemeral runtime environment on worker host

### Open Job Description (OpenJD)

OpenJD is a portable, open specification for defining batch processing jobs:

- **Portable**: Run across different systems and technology stacks
- **Human Readable**: JSON/YAML format, easily authored with text editor
- **Expressive**: General features for diverse workflows
- **Tooling Parseable**: Machine-readable for automation

## Kiro IDE Setup

This project is optimized for use with Kiro IDE and includes steering rules for AWS Deadline Cloud expertise.

### MCP Server Configuration

This project uses three MCP servers configured in `.kiro/settings/mcp.json`:

1. **AWS Documentation MCP Server**: Search and read AWS documentation
2. **Fetch MCP Server**: Fetch content from URLs
3. **AWS CDK MCP Server**: CDK guidance, Solutions Constructs, GenAI constructs, and CDK Nag rules

**Workspace Level** (`.kiro/settings/mcp.json`):
```json
{
  "mcpServers": {
    "awslabs.aws-documentation-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR",
        "AWS_DOCUMENTATION_PARTITION": "aws"
      },
      "disabled": false,
      "autoApprove": ["search_documentation", "read_documentation"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "env": {},
      "disabled": false,
      "autoApprove": ["fetch"]
    },
    "awslabs.cdk-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.cdk-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": [
        "CDKGeneralGuidance",
        "GetAwsSolutionsConstructPattern",
        "SearchGenAICDKConstructs",
        "ExplainCDKNagRule"
      ]
    }
  }
}
```

**Prerequisites:**
- Install `uv` and `uvx`: https://docs.astral.sh/uv/getting-started/installation/
- Restart Kiro or reconnect MCP servers from the MCP Server view

### Steering Rules

The project includes two steering documents in `.kiro/steering/`:

- `basic.md`: General development conventions (Python, Git, project structure)
- `deadline-cloud.md`: AWS Deadline Cloud and OpenJD expertise

These provide context to Kiro for better assistance with Deadline Cloud development.

## Getting Started

### 1. Clone the Repository

```bash
# Option 1: Clone with submodules
git clone --recurse-submodules <repo-url>

# Option 2: If already cloned, initialize submodules
git submodule update --init --recursive
```

### 2. Set Up AWS Credentials

```bash
aws configure
```

### 3. Create a Farm

```bash
aws deadline create-farm --display-name "MyFarm"
```

### 4. Create Queue and Fleet

```bash
# Create queue
aws deadline create-queue --farm-id <farm-id> --display-name "MyQueue"

# Create service-managed fleet
aws deadline create-fleet --farm-id <farm-id> --display-name "MyFleet" \
  --configuration serviceManaged={...}
```

### 5. Submit a Job

```bash
deadline bundle submit <job-bundle-directory>
```

## OpenJD Resources

The `reference/openjd-specifications` folder contains:

- OpenJD specification documentation
- Sample job templates
- Design tenets and best practices
- How jobs are constructed and run

## Fleet Types

### Service-Managed Fleets
- AWS manages infrastructure, scaling, and patching
- Supports On-Demand, Spot, and Wait and Save instances
- Easiest to set up and maintain

### Customer-Managed Fleets
- Full control over EC2 instances, AMIs, and configuration
- Manage your own Auto Scaling groups
- More flexibility for custom requirements

## Permissions

Four access levels via IAM Identity Center:

1. **Viewer**: Read-only access
2. **Contributor**: Submit jobs
3. **Manager**: Edit jobs and grant permissions
4. **Owner**: Manage budgets and view usage

## Monitoring

- **Deadline Cloud Monitor**: Web UI for job management and monitoring
- **CloudWatch**: Metrics, logs, and alarms
- **Usage Explorer**: Cost and usage estimates

## Best Practices

- Use service-managed fleets for simplicity
- Leverage queue environments for shared setup
- Set appropriate job priorities
- Configure budgets to control costs
- Use Spot/Wait and Save instances for cost optimization
- Implement path mapping for cross-platform compatibility
- Tag resources for cost tracking

## Documentation

- [AWS Deadline Cloud Documentation](https://docs.aws.amazon.com/deadline-cloud/)
- [OpenJD Specification](https://github.com/OpenJobDescription/openjd-specifications)
- [OpenJD Wiki](https://github.com/OpenJobDescription/openjd-specifications/wiki)

## Development

This project follows these conventions:

- Python 3.13 with virtual environments (`.venv`)
- All changes tracked in `changelog.md`
- Conventional Commits for git messages
- Tests in `/tests`, scripts in `/scripts`, docs in `/docs`

## License

See LICENSE file for details.
