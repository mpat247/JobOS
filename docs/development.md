# Development Setup

## Prerequisites

Before setting up JobOS for development, ensure you have the following installed:

- **Node.js** (v18.0 or higher)
- **Python** (v3.11 or higher)
- **Docker** and **Docker Compose**
- **Git**
- **Redis** (for local development without Docker)

## Environment Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/mpat247/JobOS.git
cd JobOS
```

### 2. Environment Variables

Create environment files for both services:

#### Root `.env` file

```bash
cp .env.example .env
```

Configure the following variables:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/jobos

# Redis
REDIS_URL=redis://localhost:6379

# Ollama (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Environment
NODE_ENV=development
DEBUG=true
```

#### Frontend environment (`app/.env.local`)

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend environment (`scraper/.env`)

```env
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://username:password@localhost:5432/jobos
REDIS_URL=redis://localhost:6379
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OLLAMA_BASE_URL=http://localhost:11434
```

## Supabase Setup

### 1. Create Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note your project URL and anon key from the project settings
3. Create a service role key from the project API settings

### 2. Database Schema

Run the following SQL in your Supabase SQL editor:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create roles table
CREATE TABLE roles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default roles
INSERT INTO roles (name) VALUES ('user'), ('admin');

-- Create profiles table
CREATE TABLE profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    role_id UUID REFERENCES roles(id) DEFAULT (SELECT id FROM roles WHERE name = 'user'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create companies table
CREATE TABLE companies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT,
    career_page TEXT,
    country TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create jobs table
CREATE TABLE jobs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    location TEXT,
    description TEXT,
    extracted_fields JSONB DEFAULT '{}',
    posted_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create profile trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (user_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

### 3. Authentication Setup

1. Enable Google OAuth in Supabase Auth settings
2. Configure redirect URLs:
   - Development: `http://localhost:3000/auth/callback`
   - Production: `https://yourdomain.com/auth/callback`

## Local Development

### Option 1: Docker Compose (Recommended)

This method sets up all services with their dependencies:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Access points:

- Frontend: <http://localhost:3000>
- Django API: <http://localhost:8000>
- Redis: <http://localhost:6379>

### Option 2: Manual Setup

For more control during development:

#### 1. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally (macOS)
brew install redis
brew services start redis

# Or install locally (Ubuntu)
sudo apt-get install redis-server
sudo systemctl start redis
```

#### 2. Setup Backend (Django)

```bash
cd scraper

# Create virtual environment
python -m venv jobos-venv
source jobos-venv/bin/activate  # On Windows: jobos-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Celery worker (in separate terminal)
celery -A scraperproject worker --loglevel=info

# Start Django server
python manage.py runserver 8000
```

#### 3. Setup Frontend (Next.js)

```bash
cd app

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Setup Ollama (Local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama2
ollama pull mistral

# Start Ollama service
ollama serve
```

## Development Workflow

### 1. Database Operations

```bash
# Django migrations
cd scraper
python manage.py makemigrations
python manage.py migrate

# Reset database
python manage.py flush
```

### 2. Testing

#### Frontend Tests

```bash
cd app
npm run test          # Run tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

#### Backend Tests

```bash
cd scraper
python manage.py test                    # Run all tests
python manage.py test discovery          # Test specific app
pytest --cov=discovery                   # Coverage with pytest
```

### 3. Code Quality

#### Frontend

```bash
cd app
npm run lint          # ESLint
npm run lint:fix      # Auto-fix issues
npm run type-check    # TypeScript check
npm run format        # Prettier formatting
```

#### Backend

```bash
cd scraper
black .               # Code formatting
flake8 .              # Linting
mypy .                # Type checking
```

### 4. Database Seeding

```bash
cd scraper
python manage.py shell

# In Django shell
from discovery.models import Company, Job
Company.objects.create(name="TechCorp", country="Canada", website="https://techcorp.com")
```

## Development Tools

### 1. VS Code Extensions

Recommended extensions for optimal development experience:

- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Docker
- GitLens

### 2. Browser Extensions

- React Developer Tools
- Redux DevTools
- Supabase Extension

### 3. Database Tools

- Supabase Dashboard (built-in)
- TablePlus or DBeaver for advanced database management
- Redis Commander for Redis inspection

## Debugging

### Frontend Debugging

```bash
# Enable detailed Next.js debugging
DEBUG=* npm run dev

# TypeScript type checking
npm run type-check
```

### Backend Debugging

```bash
# Django with detailed logging
DEBUG=True python manage.py runserver

# Celery with debugging
celery -A scraperproject worker --loglevel=debug

# Interactive debugging with pdb
import pdb; pdb.set_trace()
```

### Network Debugging

```bash
# Check service connectivity
curl http://localhost:3000/api/health
curl http://localhost:8000/api/health

# Redis connection
redis-cli ping
```

## Common Issues

### 1. Port Conflicts

If ports are already in use:

```bash
# Find process using port
lsof -i :3000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### 2. Database Connection Issues

```bash
# Check Supabase connection
psql "postgresql://username:password@host:port/database"

# Test environment variables
echo $DATABASE_URL
```

### 3. Node Module Issues

```bash
cd app
rm -rf node_modules package-lock.json
npm install
```

### 4. Python Environment Issues

```bash
cd scraper
deactivate
rm -rf jobos-venv
python -m venv jobos-venv
source jobos-venv/bin/activate
pip install -r requirements.txt
```

## Performance Optimization

### Development Mode Optimizations

```bash
# Next.js with faster builds
cd app
npm run dev:turbo

# Django with auto-reload disabled for large projects
cd scraper
python manage.py runserver --noreload
```

### Memory Usage

Monitor memory usage during development:

```bash
# Docker container stats
docker stats

# Python memory profiling
pip install memory-profiler
python -m memory_profiler your_script.py
```

This setup provides a complete development environment for JobOS with all necessary tools and configurations.
