You are a senior software architect. Based on the PRD in `docs/prd.md` and `docs/tech-stack.md`, create a Software Design Document that defines the overall architecture and key system decisions.

Read the PRD first, then create an SDD and save it to `docs/system-design.md`:

## Software Design Document: {System Name}

### Overview
- **Purpose**: System objectives and scope from PRD
- **Stakeholders**: Who this document serves
- **Key Requirements**: Non-functional requirements from PRD

### System Architecture
#### High-Level Design
```
User → Load Balancer → API Gateway → Services → Database
                  ↓
            Message Queue → Background Jobs
```

#### Core Components
- **API Layer**: Request handling, validation, authentication
- **Business Logic**: Core domain services and workflows
- **Data Layer**: Storage, retrieval, caching strategy
- **Integration Layer**: External system connections
- **Infrastructure**: Deployment and operations

#### Data Architecture
- **Core Entities**: Main domain objects and relationships
- **Storage Strategy**: Database choices and data modeling
- **Data Flow**: How information moves through the system
- **Backup & Recovery**: Data protection and business continuity

### Key Architectural Decisions Required
#### Infrastructure Decisions
- [ ] **Deployment Platform**: Cloud provider and container strategy
- [ ] **Load Balancing**: ALB vs API Gateway vs reverse proxy
- [ ] **Container Orchestration**: Kubernetes vs Docker Compose
- [ ] **CI/CD Pipeline**: GitHub Actions vs alternatives

#### Application Decisions  
- [ ] **API Framework**: FastAPI vs Django vs alternatives
- [ ] **Database**: PostgreSQL vs alternatives for this use case
- [ ] **Caching Strategy**: Redis vs alternatives
- [ ] **Message Queue**: For async processing if needed

#### Observability Decisions
- [ ] **Monitoring**: Prometheus/Grafana vs cloud-native
- [ ] **Logging**: Structured logging approach
- [ ] **Tracing**: Distributed tracing if microservices
- [ ] **Alerting**: On-call and notification strategy

### Performance & Scalability
- **Expected Load**: Traffic patterns from PRD success metrics
- **Scaling Strategy**: Horizontal vs vertical scaling approach
- **Performance Targets**: SLA requirements from PRD
- **Bottleneck Analysis**: Potential scaling limitations

### Security & Compliance
- **Authentication**: User identity and session management
- **Authorization**: Access control and permissions
- **Data Protection**: Encryption and privacy requirements
- **Compliance**: Regulatory requirements from PRD

Identify specific architectural choices we need to make and document as ADRs.

Think Harder