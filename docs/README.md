# Documentation Overview

This directory contains technical documentation for the Mac AI Service project.

## Service Documentation

Documentation for individual services and components:

- [**aiproxysrv**](../aiproxysrv/README.md) - Backend API service (FastAPI/Python)
- [**aiwebui**](../aiwebui/README.md) - Angular 18 frontend application
- [**forwardproxy**](../forwardproxy/README.md) - Nginx reverse proxy configuration
- [**ollamasrv**](../ollamasrv/README.md) - Ollama LLM backend service

## Architecture Documentation

Comprehensive architectural documentation following the ARC42 template:

- [**ARC42 Architecture Documentation**](arch42/README.md) - Complete system architecture including:
  - System overview and context
  - Building blocks and components
  - Runtime views and workflows
  - Deployment architecture
  - Database schema
  - Quality requirements

## Development Guides

Technical guides for developers:

- [**Database Implementation & Migrations**](DB_IMPL_DEVS.md) - SQLAlchemy models and Alembic migration workflow
- [**Docker/Colima Installation**](DOCKER-INSTALL.md) - Container runtime setup for macOS
- [**ESLint Configuration**](LINT_README.md) - Linting rules and configuration for Angular frontend
- [**OpenAPI/Swagger Implementation**](OPENAPI_IMPL_DEFS.md) - API documentation setup and standards
- [**User Management Setup**](README_USER_SETUP.md) - Initial user creation and authentication

## Quick Start

For a quick overview of the system architecture, start with the [ARC42 Architecture Documentation](arch42/README.md).

For service-specific setup and development instructions, refer to the individual service README files linked above.
