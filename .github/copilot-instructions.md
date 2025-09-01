<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI-Powered Retail Analytics Platform - Copilot Instructions

## Project Overview
This is a comprehensive retail analytics platform that combines full-stack development with AI/ML capabilities. The project demonstrates:

- **Backend**: FastAPI with PostgreSQL, SQLAlchemy ORM, machine learning with scikit-learn
- **Frontend**: React with TypeScript, TailwindCSS, and modern data visualization
- **AI Integration**: OpenAI API for natural language report generation
- **ML Features**: Sales prediction, inventory optimization, customer insights

## Code Style and Conventions

### Backend (Python/FastAPI)
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions (snake_case for variables/functions, PascalCase for classes)
- Use Pydantic models for request/response validation
- Implement proper error handling with HTTPException
- Use dependency injection for database sessions
- Keep business logic in service classes
- Use async/await for I/O operations

### Frontend (React/TypeScript)
- Use functional components with hooks
- Implement proper TypeScript typing for all props and state
- Use React Query for server state management
- Follow component composition patterns
- Use TailwindCSS utility classes for styling
- Implement proper error boundaries and loading states
- Use custom hooks for reusable logic

### Database Design
- Use descriptive table and column names
- Implement proper foreign key relationships
- Add indexes for frequently queried columns
- Use timestamps for audit trails
- Follow normalization principles

### Machine Learning
- Document model features and assumptions
- Implement proper data validation and preprocessing
- Use versioning for models
- Add performance monitoring and metrics
- Implement graceful fallbacks when models fail

## Key Architecture Patterns

1. **API Design**: RESTful endpoints with consistent response formats
2. **Data Flow**: Unidirectional data flow from API → React Query → Components
3. **Error Handling**: Consistent error responses with proper HTTP status codes
4. **Authentication**: JWT-based authentication with refresh tokens
5. **Validation**: Input validation at both frontend and backend levels

## Development Guidelines

- Write comprehensive tests for business logic
- Use environment variables for configuration
- Implement proper logging for debugging
- Follow security best practices (input sanitization, authentication)
- Document complex business logic
- Use meaningful commit messages
- Keep components and functions focused on single responsibilities

## Specific Context

When working on this project, consider:

- **Business Domain**: Retail operations, sales analysis, inventory management
- **User Personas**: Store managers, business analysts, executives
- **Performance**: Handle large datasets efficiently
- **Scalability**: Design for growth in data volume and user base
- **AI Integration**: Balance automation with human oversight
- **Data Privacy**: Protect customer and business data

## Common Tasks

- Adding new analytics endpoints
- Creating data visualization components
- Implementing ML model improvements
- Building AI-powered report generation
- Optimizing database queries
- Adding new business metrics
- Improving user experience flows
