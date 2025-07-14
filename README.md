# JobOS

JobOS is a full-stack AI-powered job discovery and resume optimization platform that enables users to search for companies, automatically discover and scrape career pages, and view structured job listings with intelligent matching capabilities.

## Features

- **Company Search**: Search for any company by name and country to discover jobs
- **Intelligent Career Page Discovery**: Automatically locate career pages using AI-powered search
- **Job Scraping**: Extract structured job data from various job board platforms (Lever, Workday, Greenhouse)
- **AI-Powered Parsing**: Convert job listings to structured format using LLMs
- **Resume Optimization**: AI-powered resume matching and optimization (planned)
- **Real-time Updates**: Background workers for continuous job discovery

## Tech Stack

### Frontend

- **Framework**: Next.js 14 (App Router, SSR)
- **Styling**: Tailwind CSS + shadcn/ui
- **Authentication**: Supabase Auth with Google OAuth
- **State Management**: Redux Toolkit

### Backend

- **Scraper Service**: Django with Python 3.11
- **Web Crawling**: Playwright + Crawl4AI
- **AI Processing**: LangChain with Ollama
- **Task Queue**: Celery + Redis
- **Database**: Supabase PostgreSQL

### Infrastructure

- **Containerization**: Docker + Docker Compose
- **Registry**: AWS Elastic Container Registry (ECR)
- **Deployment**: AWS App Runner
- **CI/CD**: GitHub Actions

## Project Structure

```text
JobOS/
├── app/                    # Next.js frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # App router pages
│   │   ├── lib/            # Utilities and Supabase clients
│   │   └── services/       # API service layer
│   └── Dockerfile
├── scraper/                # Django backend service
│   ├── discovery/          # Job discovery Django app
│   ├── helpers/            # Scraping utilities
│   └── testscripts/        # Development and testing scripts
├── docs/                   # Project documentation
└── docker-compose.yml     # Multi-service orchestration
```

## Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/mpat247/JobOS.git
   cd JobOS
   ```

2. **Environment Setup**

   ```bash
   cp .env.example .env
   # Configure your Supabase credentials and other environment variables
   ```

3. **Start with Docker Compose**

   ```bash
   docker-compose up --build
   ```

4. **Access the application**

   - Frontend: <http://localhost:3000>
   - Django Admin: <http://localhost:8000/admin>

## Documentation

Detailed documentation is available in the `/docs` directory:

- [Technical Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Development Setup](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## Current Status

JobOS is actively under development. Core features include company search, career page discovery, and basic job scraping. Advanced AI features and resume optimization are planned for upcoming releases.
