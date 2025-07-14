# Technical Architecture

## System Overview

JobOS is designed as a microservices architecture with separate frontend and backend services, orchestrated through Docker Compose and deployed on AWS infrastructure.

## Architecture Diagram

```text
[Next.js Frontend]
    |
    |--- User Auth (Supabase)
    |--- Job Viewer + Company Search
    |
[API Routes]
    |
    |--- /api/scrape → Triggers Celery Job
    |
[Django Scraper Backend]
    |
    |--- DuckDuckGo/Playwright + Crawl4AI
    |--- LangChain HTML Parsing
    |
    |--- Celery Worker → Fetch Career Page
    |                  → Extract & Normalize Jobs
    |
[Supabase Postgres DB]
    |
    |--- users / profiles / roles
    |--- companies / jobs
    |--- job_history (version tracking)
    |
[Storage / Extras]
    |
    |--- Supabase Storage (for resumes)
    |--- Redis (for Celery queues)
    |--- Ollama or Local LLMs
```

## Core Components

### Frontend Application (Next.js)

**Location**: `/app`

- **Framework**: Next.js 14 with App Router
- **Authentication**: Supabase Auth with Google OAuth integration
- **State Management**: Redux Toolkit for global state
- **UI Components**: Tailwind CSS with shadcn/ui component library
- **Routing**: File-based routing with middleware for auth protection

**Key Features**:

- Server-side rendering for SEO optimization
- Protected routes with middleware authentication
- Real-time updates through Supabase subscriptions
- Responsive design for mobile and desktop

### Backend Scraper Service (Django)

**Location**: `/scraper`

- **Framework**: Django 4.x with Django REST Framework
- **Task Queue**: Celery with Redis broker
- **Web Crawling**: Playwright for JavaScript-heavy sites
- **Content Processing**: Crawl4AI for intelligent content extraction
- **AI Integration**: LangChain with Ollama for content parsing

**Key Modules**:

- `discovery/`: Core Django app for job discovery
- `helpers/`: Utility modules for scraping and parsing
- `testscripts/`: Development and testing utilities

### Database Layer (Supabase PostgreSQL)

**Core Tables**:

- `profiles`: User profile information with role-based access
- `companies`: Company information and career page URLs
- `jobs`: Structured job listings with metadata
- `roles`: User permission levels
- `job_history`: Version tracking for job changes (planned)

### Infrastructure Services

**Task Queue**: Redis + Celery

- Asynchronous job processing
- Retry logic for failed scraping tasks
- Background refresh of job listings

**Storage**: Supabase Storage

- Resume document storage
- Processed job data caching
- User-generated content

## Data Flow

### Job Discovery Process

1. **User Input**: Company name and country selection
2. **Search Initiation**: Frontend triggers `/api/scrape/company`
3. **Career Page Discovery**: Playwright searches DuckDuckGo for career pages
4. **Content Extraction**: Crawl4AI processes page content to markdown
5. **Job Parsing**: LangChain + Ollama extract structured job data
6. **Storage**: Normalized job data saved to Supabase
7. **UI Update**: Frontend displays processed job listings

### Authentication Flow

1. **OAuth Login**: User authenticates via Google through Supabase
2. **Profile Creation**: Automatic profile creation with default role
3. **Session Management**: JWT token handling for API access
4. **Route Protection**: Middleware validates authentication for protected pages

## Scalability Considerations

### Horizontal Scaling

- Frontend: Stateless Next.js instances behind load balancer
- Backend: Multiple Django workers processing Celery tasks
- Database: Supabase handles PostgreSQL scaling automatically

### Performance Optimization

- **Caching**: Redis for frequent data access
- **CDN**: Static assets served through AWS CloudFront
- **Database Indexing**: Optimized queries for job search and filtering
- **Background Processing**: Non-blocking UI through async task queues

## Security Architecture

### Authentication & Authorization

- OAuth 2.0 through Supabase Auth
- Role-based access control (RBAC)
- JWT token validation on API requests
- Secure session management

### Data Protection

- Environment variable management for secrets
- HTTPS/TLS encryption for all communications
- Input validation and sanitization
- Rate limiting for API endpoints

## Monitoring & Logging

### Application Monitoring

- Health checks for all services
- Performance metrics collection
- Error tracking and alerting
- Resource usage monitoring

### Logging Strategy

- Structured logging with Winston (frontend)
- Django logging framework (backend)
- Centralized log aggregation
- Debug and audit trails

## Deployment Architecture

### Containerization

- Docker containers for consistent environments
- Multi-stage builds for optimized images
- Docker Compose for local development

### AWS Infrastructure

- **ECR**: Container image registry
- **App Runner**: Serverless container deployment
- **GitHub Actions**: CI/CD pipeline automation
- **Route 53**: DNS management
- **CloudFront**: CDN for static assets

### Environment Management

- Development: Local Docker Compose
- Staging: AWS App Runner with test database
- Production: AWS App Runner with production Supabase
