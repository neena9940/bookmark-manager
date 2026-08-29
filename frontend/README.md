# 🔖 Bookmark Manager Pro

A production-grade, AI-powered bookmark management system built with modern async Python.

## ✨ Features

- **🤖 AI-Powered Summaries**: Automatic bookmark summarization using Ollama (Llama 3.2)
- ** Async Architecture**: Built with FastAPI and SQLAlchemy async for maximum performance
- **🔐 Enterprise Auth**: JWT access tokens + refresh tokens with role-based access control
- **📦 Background Jobs**: ARQ + Redis for asynchronous task processing
- **💾 Smart Caching**: Redis caching for 50x faster query responses
- **️ File Storage**: S3-compatible storage (MinIO) for screenshots
- **🏷️ Rich Tagging**: Many-to-many tag relationships with full-text search
- **📊 Pagination**: Efficient data loading with customizable page sizes
- **🛡️ Rate Limiting**: Protection against brute-force attacks
- **🗑️ Soft Deletes**: Data recovery and audit trails

## 🏗️ Architecture
