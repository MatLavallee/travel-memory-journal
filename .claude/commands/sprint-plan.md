You are a senior engineering manager. Based on the approved PRD, SDD, and ADRs, break down the work into 3 sprints that each deliver functional increments.

Read `docs/prd.md`, `docs/system-design.md`, and `docs/adr/*.md` first.

Create a sprint plan and save it to `docs/sprint-plan.md`:

# Sprint Planning: {Project Name}

## Overall Strategy
**MVP Goal**: {Core user value from PRD}
**Technical Foundation**: {Key architectural decisions from ADRs}
**User Journey**: {End-to-end flow we're building toward}

## Sprint 1: Foundation & Core Workflow (2 weeks)
**Sprint Goal**: Users can {core action from PRD} end-to-end

**Jobs to be Done**:
- As a user, I can {primary user story from PRD}
- As a developer, I have a solid foundation for future features
- As a business, I can demonstrate core value proposition

**Deliverables**:
- [ ] Authentication system (login/logout/registration)
- [ ] Core API endpoints with validation
- [ ] Database schema and basic CRUD operations
- [ ] Simple frontend interface for main workflow
- [ ] Basic error handling and user feedback
- [ ] CI/CD pipeline and deployment
- [ ] Health checks and basic monitoring

## Sprint 2: Enhanced Functionality (2 weeks)
**Sprint Goal**: Users have a complete, polished experience

**Jobs to be Done**:
- As a user, I can {secondary user stories from PRD}
- As a business, I can track user engagement
- As a developer, I can monitor system health

**Deliverables**:
- [ ] Additional user workflows from PRD
- [ ] Data validation and business rules
- [ ] Improved UI/UX with better error handling
- [ ] User analytics and usage tracking
- [ ] Performance optimizations
- [ ] Comprehensive test coverage
- [ ] Documentation for users and developers

## Sprint 3: Scale & Polish (2 weeks)  
**Sprint Goal**: Production-ready system that can scale

**Jobs to be Done**:
- As a user, I have a fast, reliable experience
- As a business, I can scale to more users
- As a developer, I can maintain and extend the system

**Deliverables**:
- [ ] Performance monitoring and alerting
- [ ] Caching and optimization
- [ ] Advanced error handling and recovery
- [ ] Admin tools and operational dashboards
- [ ] Security hardening
- [ ] Load testing and capacity planning
- [ ] Production runbooks and documentation

Focus on delivering complete user value in each sprint.

Think Hardest