# Portfolio & Resume Generation Platform

A comprehensive platform that enables users to create detailed professional profiles and generate AI-optimized resumes tailored to specific job requirements.

## 🚀 Features

- **User Profile Management**: Comprehensive profile with education, experience, skills, and contact information
- **Project Portfolio**: Rich project showcase with media, descriptions, and technology tags
- **AI-Powered Optimization**: Intelligent resume optimization based on job descriptions
- **LaTeX Template System**: Professional LaTeX templates with customization options
- **Secure File Management**: Upload and manage certificates, documents, and portfolio pieces
- **Multiple Export Formats**: PDF generation and LaTeX source export
- **ATS Optimization**: Ensure resume compatibility with Applicant Tracking Systems

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React.js 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python) + Supabase Auth + PostgreSQL
- **Storage**: S3-compatible storage for files and media
- **AI/ML**: Keyword extraction and content optimization
- **LaTeX Engine**: Template rendering and PDF compilation

### Project Structure
```
resume-twin-platform/
├── frontend/           # React.js application
├── backend/            # FastAPI application
├── database/           # Database schemas and migrations
├── templates/          # LaTeX resume templates
├── docs/              # Project documentation
├── tests/             # Test suites
└── docker/            # Docker configuration
```

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Astral UV for Python package management
- Docker and Docker Compose (optional)

### Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd resume-twin-platform
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Backend Setup**
   ```bash
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload --port 8000
   ```

4. **Environment Variables**
   Create `.env` files in both frontend and backend directories with:
   ```bash
   # Backend (.env)
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   DATABASE_URL=your_database_url
   S3_BUCKET_NAME=your_s3_bucket
   S3_ACCESS_KEY=your_s3_access_key
   S3_SECRET_KEY=your_s3_secret_key
   
   # Frontend (.env)
   VITE_API_URL=http://localhost:8000
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

## 📋 Development Status

### ✅ Phase 1-6: Foundation & Core Features (COMPLETED)
- [x] Project structure and documentation
- [x] Development environment with Docker
- [x] Database schema with PostgreSQL + Supabase
- [x] Authentication system with JWT
- [x] FastAPI backend with comprehensive endpoints
- [x] File management with S3 storage
- [x] LaTeX template system with PDF generation
- [x] React frontend with Tailwind CSS v4

### ✅ Phase 7: AI-Powered Resume Optimization (COMPLETED)
- [x] OpenRouter AI integration with circuit breaker
- [x] Job description analysis endpoint
- [x] Resume content optimization
- [x] Skills gap analysis
- [x] ATS compatibility checking
- [x] Real-time profile data integration

### ✅ Phase 8: User Profile Management (COMPLETED)
- [x] Complete profile CRUD operations
- [x] Education management endpoints
- [x] Professional experience tracking
  - Certifications with expiry tracking
  - Internships with company details
  - Courses with completion status
  - Activities with impact metrics
- [x] Profile completion scoring
- [x] Data validation with Pydantic

### ✅ Phase 9: Project Management System (COMPLETED)
- [x] Project CRUD with filtering
- [x] Media upload and management
- [x] Technology stack tracking
- [x] Featured project highlighting
- [x] Project status workflows
- [x] Rich project metadata

### ✅ Phase 10: Integration Testing (COMPLETED)
- [x] Profile workflow integration tests
- [x] AI optimization integration tests
- [x] End-to-end test scenarios
- [x] Mock AI responses for testing
- [x] Comprehensive test fixtures

### ✅ Phase 11: Deployment & Documentation (COMPLETED)
- [x] Production deployment guide
  - Railway backend deployment
  - Vercel frontend deployment
  - Docker containerization
  - Manual server setup
- [x] Complete API documentation
- [x] Environment configuration guides
- [x] Security best practices
- [x] Monitoring and backup strategies

### 🚀 Future Enhancements (Planned)
- [ ] **Analytics Dashboard**: Track resume views, downloads, and application success rates
- [ ] **Template Marketplace**: Community-contributed resume templates
- [ ] **Collaborative Reviews**: Share resumes with mentors for feedback
- [ ] **Interview Prep**: AI-powered interview question generation based on job description
- [ ] **Career Path Recommendations**: Suggest roles based on skills and experience
- [ ] **Resume A/B Testing**: Compare different resume versions
- [ ] **Browser Extension**: Quick-apply to jobs with auto-filled resumes
- [ ] **Mobile Applications**: Native iOS and Android apps
- [ ] **Multi-language Support**: Internationalization for global users
- [ ] **LinkedIn Integration**: Import profile data from LinkedIn
- [ ] **Cover Letter Generator**: AI-powered cover letter creation
- [ ] **Skills Assessment**: Verify skills with quizzes and certifications

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                                    # Run all tests
pytest -v                                 # Verbose output
pytest --cov=app --cov-report=html        # Generate coverage report
pytest tests/integration/                 # Run integration tests only
pytest tests/services/test_ai_service.py  # Run specific test file
```

### Frontend Tests
```bash
cd frontend
npm test                   # Run all tests
npm run test:coverage      # With coverage report
npm run test:watch         # Watch mode
```

### Integration Test Scenarios
- **Profile Workflow**: Complete profile creation, education/experience addition, completion scoring
- **AI Optimization**: Job description analysis, resume optimization, skills gap analysis
- **End-to-End**: Full user journey from signup to resume generation

### Test Coverage
- **Backend**: 80%+ coverage across services, endpoints, and utilities
- **Frontend**: Component tests with React Testing Library
- **Integration**: Critical user workflows validated

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[API Documentation](docs/api-documentation.md)**: Complete REST API reference with request/response examples
- **[Deployment Guide](docs/deployment-guide.md)**: Production deployment instructions for Railway, Vercel, Docker
- **[Database Schema](database/schema.sql)**: PostgreSQL schema with Row Level Security policies
- **[System Design](docs/design.md)**: Architecture overview and design decisions
- **[Implementation Workflow](docs/implementation_workflow.md)**: Development phases and roadmap
- **[Supabase Setup](docs/supabase-setup-guide.md)**: Supabase configuration and integration guide
- **[System Analysis](docs/system_analysis.md)**: Technical requirements and analysis

### Quick Links
- **Interactive API Docs**: http://localhost:8000/docs (when backend is running)
- **Alternative API Docs**: http://localhost:8000/redoc

## 🚀 Deployment

### Railway (Backend) + Vercel (Frontend) - Recommended
The easiest production deployment option. See [Deployment Guide](docs/deployment-guide.md) for detailed instructions.

**Backend on Railway:**
```bash
# Connect your GitHub repository to Railway
# Set environment variables in Railway dashboard
# Deploy automatically on push
```

**Frontend on Vercel:**
```bash
cd frontend
vercel --prod
```

### Docker Deployment
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Server Deployment
See the [Deployment Guide](docs/deployment-guide.md) for:
- Nginx configuration
- SSL setup with Let's Encrypt
- Systemd service configuration
- Database backup strategies
- Monitoring with Sentry

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass (`pytest` and `npm test`)
6. Commit your changes using conventional commits
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- **Python Backend**: 
  - Follow PEP 8 style guide
  - Use Black for formatting
  - Add type hints to all functions
  - Write docstrings for public APIs
  - Maintain test coverage >80%
  
- **TypeScript Frontend**:
  - Use ESLint and Prettier
  - Follow React best practices
  - Write component tests
  - Use TypeScript strict mode
  
- **Commits**: 
  - Use conventional commits format
  - Examples: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
  - Write clear, descriptive commit messages

### Pull Request Process
1. Update documentation for any changed functionality
2. Add tests for new features
3. Ensure CI/CD pipeline passes
4. Request review from maintainers
5. Address review feedback
6. Squash commits before merge (if requested)

### Areas for Contribution
- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Additional test coverage
- 🎨 UI/UX enhancements
- ♿ Accessibility improvements
- 🌐 Internationalization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@resumetwin.com
- Documentation: [docs/](docs/)

## 🗺️ Roadmap

- [ ] Mobile app development
- [ ] Advanced AI recommendations
- [ ] Collaborative features
- [ ] Enterprise solutions
- [ ] Multi-language support

---

**Built with ❤️ for professionals worldwide**