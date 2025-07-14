# API Reference

## Overview

JobOS provides both REST API endpoints through Django and Next.js API routes for different functionalities. This document covers all available endpoints and their usage.

## Authentication

All API requests require authentication through Supabase JWT tokens unless otherwise specified.

### Headers

```text
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Next.js API Routes

### Company Search

#### POST /api/scrape/company

Initiates company career page discovery and job scraping.

**Request Body**:

```json
{
  "companyName": "string",
  "country": "string"
}
```

**Response**:

```json
{
  "success": true,
  "data": {
    "company": {
      "id": "uuid",
      "name": "string",
      "country": "string",
      "careerPage": "string"
    },
    "taskId": "string"
  }
}
```

**Status Codes**:

- `200`: Success
- `400`: Invalid request parameters
- `401`: Unauthorized
- `500`: Server error

### Job Management

#### GET /api/jobs

Retrieve job listings with optional filtering.

**Query Parameters**:

- `companyId` (optional): Filter by specific company
- `location` (optional): Filter by job location
- `title` (optional): Filter by job title
- `page` (optional): Pagination page number
- `limit` (optional): Number of results per page

**Response**:

```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "uuid",
        "title": "string",
        "location": "string",
        "description": "string",
        "companyId": "uuid",
        "extractedFields": {
          "salary": "string",
          "experience": "string",
          "skills": ["string"]
        },
        "postedDate": "date",
        "isActive": true
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

#### GET /api/jobs/[id]

Retrieve specific job details.

**Response**:

```json
{
  "success": true,
  "data": {
    "job": {
      "id": "uuid",
      "title": "string",
      "location": "string",
      "description": "string",
      "company": {
        "id": "uuid",
        "name": "string",
        "website": "string"
      },
      "extractedFields": {
        "salary": "string",
        "experience": "string",
        "skills": ["string"],
        "benefits": ["string"]
      },
      "postedDate": "date",
      "isActive": true
    }
  }
}
```

### User Profile

#### GET /api/profile

Get current user profile information.

**Response**:

```json
{
  "success": true,
  "data": {
    "profile": {
      "id": "uuid",
      "userId": "uuid",
      "fullName": "string",
      "email": "string",
      "role": {
        "id": "uuid",
        "name": "string"
      }
    }
  }
}
```

#### PUT /api/profile

Update user profile information.

**Request Body**:

```json
{
  "fullName": "string"
}
```

## Django API Endpoints

### Scraper Service

Base URL: `http://localhost:8000/api/`

#### POST /api/discovery/scrape/

Initiate job scraping for a specific company.

**Request Body**:

```json
{
  "company_name": "string",
  "country": "string",
  "career_url": "string"
}
```

**Response**:

```json
{
  "task_id": "string",
  "status": "started",
  "company_id": "uuid"
}
```

#### GET /api/discovery/scrape/status/{task_id}/

Check scraping task status.

**Response**:

```json
{
  "task_id": "string",
  "status": "pending|started|success|failure",
  "result": {
    "jobs_found": 25,
    "jobs_processed": 23,
    "errors": []
  }
}
```

#### GET /api/discovery/companies/

List all companies in the database.

**Query Parameters**:

- `search` (optional): Search company names
- `country` (optional): Filter by country

**Response**:

```json
{
  "companies": [
    {
      "id": "uuid",
      "name": "string",
      "country": "string",
      "career_page": "string",
      "last_scraped": "datetime",
      "job_count": 15
    }
  ]
}
```

### Job Board Detection

#### POST /api/discovery/detect-board/

Detect job board type for a given URL.

**Request Body**:

```json
{
  "url": "string",
  "page_content": "string"
}
```

**Response**:

```json
{
  "board_type": "lever|workday|greenhouse|smartrecruiters|bamboohr|custom",
  "confidence": 0.95,
  "supported_features": ["job_listing", "application_form", "structured_data"]
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

### Common Error Codes

- `AUTH_REQUIRED`: Authentication required
- `INVALID_REQUEST`: Request validation failed
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SCRAPING_FAILED`: Job scraping task failed
- `PARSING_ERROR`: Content parsing failed

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Authentication endpoints: 5 requests per minute
- Search endpoints: 10 requests per minute
- Data retrieval endpoints: 100 requests per minute

## Webhook Events

### Job Update Notifications

JobOS can send webhook notifications for job updates.

**Endpoint**: POST to configured webhook URL

**Payload**:

```json
{
  "event": "job.created|job.updated|job.deleted",
  "timestamp": "datetime",
  "data": {
    "job": {
      "id": "uuid",
      "title": "string",
      "company": "string"
    }
  }
}
```

## SDK and Client Libraries

### JavaScript/TypeScript

```typescript
import { JobOSClient } from "@jobos/sdk";

const client = new JobOSClient({
  apiKey: "your-api-key",
  baseUrl: "https://api.jobos.com",
});

// Search for jobs
const jobs = await client.jobs.search({
  company: "TechCorp",
  location: "Toronto",
});
```

### Python

```python
from jobos_sdk import JobOSClient

client = JobOSClient(
    api_key='your-api-key',
    base_url='https://api.jobos.com'
)

# Scrape company jobs
result = client.scraper.scrape_company(
    company_name='TechCorp',
    country='Canada'
)
```

## Testing

### API Testing

Use the provided test scripts in `/scraper/testscripts/` for API testing:

```bash
cd scraper/testscripts
python test_api.py
```

### Postman Collection

Import the Postman collection from `/docs/postman/jobos-api.json` for interactive API testing.
