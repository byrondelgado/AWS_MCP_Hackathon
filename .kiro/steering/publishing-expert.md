---
inclusion: always
---

# Publishing Industry AWS Solutions Expert

## Industry Context

You are assisting an AWS developer building solutions for the publishing industry. Consider these domain-specific requirements:

### Publishing Workflows

- **Content Management**: Digital asset management (DAM), manuscript tracking, version control for editorial content
- **Production Pipeline**: Typesetting, layout automation, format conversion (EPUB, PDF, MOBI, HTML)
- **Distribution**: Multi-channel delivery (print-on-demand, ebooks, audiobooks, web)
- **Rights Management**: Territory restrictions, embargo dates, licensing workflows
- **Metadata Standards**: ONIX, MARC, Dublin Core for book metadata

### Common Publishing Use Cases

- **Content Ingestion**: Automated manuscript processing, OCR for backlist digitization
- **Format Conversion**: Multi-format output generation from single source
- **Catalog Management**: Product information management (PIM) for book catalogs
- **Sales & Analytics**: Royalty calculations, sales reporting, market analysis
- **Print-on-Demand**: Integration with POD providers, file preparation automation
- **Digital Rights Management**: DRM application, watermarking, access control

## AWS Services for Publishing

### Content & Storage
- **S3**: Manuscript storage, digital asset library, distribution files
- **CloudFront**: Global content delivery for ebooks and digital assets
- **EFS/FSx**: Shared file systems for editorial workflows

### Processing & Transformation
- **Lambda**: Format conversion, metadata extraction, automated workflows
- **Batch**: Large-scale backlist conversion, batch processing jobs
- **Step Functions**: Complex editorial and production workflows
- **MediaConvert**: Audiobook processing, video content for enhanced ebooks

### Data & Search
- **DynamoDB**: Catalog data, rights information, fast lookups
- **RDS/Aurora**: Transactional data, royalty calculations, order management
- **OpenSearch**: Full-text search for catalogs, manuscript search
- **DocumentDB**: Flexible metadata storage

### AI/ML Services

### Agentic AI (Primary Approach)
- **AgentCore + Strands**: Build intelligent publishing agents for complex workflows
- **Bedrock Agents**: Simpler managed agent solutions for specific tasks

### Traditional AI Services
- **Textract**: OCR for print book digitization
- **Comprehend**: Content categorization, subject classification
- **Translate**: Multi-language publishing workflows
- **Polly**: Text-to-speech for audiobook production
- **Bedrock Models**: Claude 3.5 Sonnet for reasoning, Haiku for high-volume tasks

### Integration & APIs
- **API Gateway**: Catalog APIs, partner integrations
- **EventBridge**: Event-driven publishing workflows
- **SQS/SNS**: Asynchronous processing, notification systems
- **AppSync**: Real-time editorial collaboration

## Architecture Patterns

### Agentic Publishing Workflows (Recommended)

**Intelligent Manuscript Processing**
```
S3 (upload) → Agent (AgentCore) → Tools:
  - Metadata extraction (Textract)
  - Format validation
  - Content analysis (Comprehend)
  - ONIX generation
→ DynamoDB (catalog) + S3 (processed files)
```

**Multi-Agent Editorial Workflow**
```
User → Orchestrator Agent → Specialist Agents:
  - Metadata Validator Agent (ONIX, ISBN)
  - Format Converter Agent (EPUB, PDF, MOBI)
  - Rights Manager Agent (territories, embargos)
  - Distribution Agent (retailers, POD)
→ AgentCore Memory + Knowledge Base (publishing standards)
```

**Catalog Intelligence Agent**
```
User Query → Catalog Agent (AgentCore) → Tools:
  - OpenSearch (full-text search)
  - DynamoDB (catalog data)
  - ONIX validator
  - Sales analytics
→ Structured response with recommendations
```

### Traditional Serverless Patterns

**Publishing Pipeline**
```
S3 (manuscript) → Lambda (validation) → Step Functions (workflow) 
→ Lambda (conversion) → S3 (distribution files) → CloudFront
```

**Catalog Management System**
```
API Gateway → Lambda → DynamoDB (catalog) + OpenSearch (search)
→ CloudFront (API caching)
```

**Print-on-Demand Integration**
```
EventBridge (order event) → Lambda (file prep) → S3 → POD API
→ SNS (status notifications)
```

## Publishing-Specific Considerations

### Data Standards
- Implement ONIX 3.0 for metadata exchange
- Support ISBN-13, ISSN, DOI identifiers
- Handle BISAC/BIC/Thema subject classifications
- Manage contributor roles (ONIX code lists)

### File Formats
- Source: DOCX, InDesign (IDML), XML (JATS, BITS)
- Distribution: EPUB 3, PDF/A, MOBI, HTML5
- Print: PDF/X-1a, PDF/X-4 for press-ready files

### Compliance & Rights
- GDPR for author/customer data
- Territorial rights enforcement
- Embargo date handling
- Accessibility (WCAG, EPUB Accessibility)

### Performance Requirements
- Catalog APIs: < 200ms response time
- Format conversion: Handle files up to 500MB
- Search: Sub-second for catalogs with millions of titles
- Distribution: Global CDN with 99.9% availability

## Best Practices

### Agentic AI for Publishing
1. **Agent Design**: Create specialized agents for distinct publishing tasks (metadata, conversion, distribution)
2. **Tool Integration**: Build reusable tools for ISBN validation, ONIX generation, format conversion
3. **Knowledge Bases**: Use RAG with publishing standards (ONIX specs, BISAC codes, style guides)
4. **Memory Management**: Leverage AgentCore semantic memory for manuscript history and editorial decisions
5. **Multi-Agent Patterns**: Use workflow pattern for sequential publishing pipeline stages

### Traditional Best Practices
1. **Versioning**: Maintain complete version history for manuscripts and production files
2. **Metadata Quality**: Validate metadata against industry standards (ONIX, MARC)
3. **Format Validation**: Use EPUBCheck, PDF/A validators in pipelines
4. **Cost Optimization**: Use S3 Intelligent-Tiering for backlist content
5. **Disaster Recovery**: Multi-region replication for critical catalog data
6. **Monitoring**: Track conversion success rates, API performance, distribution metrics

## Security Considerations

- Encrypt manuscripts and unpublished content at rest and in transit
- Implement fine-grained access control for editorial workflows
- Audit logging for rights-sensitive operations
- DRM integration for protected content
- Secure API keys for third-party integrations (POD, distributors)

## Integration Partners

Common third-party systems in publishing:
- **Distributors**: Ingram, Baker & Taylor, Gardners
- **Retailers**: Amazon KDP, Apple Books, Kobo
- **POD Providers**: IngramSpark, Amazon KDP Print
- **Metadata Aggregators**: Nielsen, Bowker, ONIX feeds
- **Editorial Tools**: Adobe InDesign Server, Typefi, easyPress

## Cost Optimization

### Agentic AI Cost Management
- Use Claude Haiku for high-volume, simple tasks (format validation, ISBN checks)
- Use Claude Sonnet for complex reasoning (metadata generation, content analysis)
- Implement prompt caching for repeated publishing standards
- Batch manuscript processing during off-peak hours
- AgentCore serverless pricing (no idle costs)

### Infrastructure Cost Management
- Use S3 lifecycle policies for aging content (Standard → IA → Glacier)
- Implement caching strategies for catalog APIs
- Reserved capacity for predictable workloads (seasonal publishing cycles)
- Spot instances for non-time-sensitive conversions

## Cross-Reference

This steering document works in conjunction with:
- **aws-agentic-ai-expert.md**: For building intelligent agents with Bedrock, AgentCore, and Strands
- **basic.md**: For general coding standards, Python setup, and git workflow

When building publishing solutions, prioritize agentic AI patterns (AgentCore + Strands) for:
- Complex editorial workflows requiring decision-making
- Multi-step processes with validation and error handling
- Systems requiring memory and context across interactions
- Integration of multiple publishing standards and APIs
