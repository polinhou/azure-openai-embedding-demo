# Azure OpenAI Embedding Demo with Qdrant

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)
[![Qdrant](https://img.shields.io/badge/vector%20database-qdrant-ff69b4)](https://qdrant.tech/)

This project demonstrates how to use Azure OpenAI's text embedding API with Qdrant for efficient vector search. The project is named `azure-openai-embedding-demo`.

## 🚀 Features

- Generate text embeddings using Azure OpenAI
- Store and search vectors with Qdrant
- Simple configuration via environment variables
- Containerized Qdrant with Docker Compose
- Ready for production use cases

## 📋 Prerequisites

- Docker and Docker Compose (for Qdrant)
- Python 3.11 (specifically 3.11.x is required)
- [Poetry](https://python-poetry.org/) for dependency management
- Azure subscription with OpenAI access
- [Git](https://git-scm.com/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd azure-openai-embedding-demo
```

### 2. Set Up Python Environment

```bash
# Install Python 3.11 if not already installed
# Using pyenv (recommended):
pyenv install 3.11.13
pyenv local 3.11.13

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -


# Install project dependencies
poetry install
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_deployment_name

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=lyrics
```

### 4. Create Qdrant Storage Directory

Create a local directory for Qdrant storage:

```bash
mkdir -p qdrant_storage
```

### 5. Start Qdrant with Docker

```bash
docker-compose up -d
```

The Qdrant dashboard will be available at: http://localhost:6333/dashboard

## 🏃 Running the Application

Run the demo script:

```bash
poetry run python main.py
```

This will:
- Create a Qdrant collection
- Generate embeddings for sample lyrics
- Store them in Qdrant
- Perform a similarity search

## 📝 Project Structure

```
.
├── .env.example           # Example environment variables
├── .gitignore
├── README.md              # This file
├── docker-compose.yml     # Qdrant Docker configuration
├── main.py               # Main application code
├── poetry.lock           # Poetry lock file
└── pyproject.toml        # Project metadata and dependencies
```

## 🔧 Dependencies

Key dependencies are managed by Poetry and specified in `pyproject.toml`:

- Python 3.11
- qdrant-client>=1.12.0,<1.13.0 (compatible with Qdrant 1.12.x)
- openai>=1.12.0,<2.0.0
- python-dotenv>=1.0.0,<2.0.0

## ⚠️ Important Notes

### Qdrant Client Version

This project uses `qdrant-client>=1.12.0,<1.13.0` which is compatible with Qdrant 1.12.x. The code has been updated to use the latest stable APIs.

Key changes in Qdrant 1.12:
- Improved performance and stability
- Enhanced vector search capabilities
- Updated API endpoints for better compatibility

For the most up-to-date information, please refer to the [Qdrant 1.12 Release Notes](https://github.com/qdrant/qdrant/releases/tag/v1.12.0).

## 📚 Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Poetry Documentation](https://python-poetry.org/docs/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 Development

### Running Tests

To run the tests:

```bash
poetry run pytest
```

### Updating Dependencies

To add a new dependency:

```bash
poetry add package_name
```

To update all dependencies:

```bash
poetry update
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

For any questions or suggestions, please open an issue.

## Project Structure

```
.
├── main.py                # Main application script
├── pyproject.toml         # Project dependencies and configuration
├── README.md              # This file
├── .env.example           # Example environment variables
└── .gitignore             # Git ignore rules
```

## Development

### Adding New Features

1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```

2. Run tests:
   ```bash
   poetry run pytest
   ```

3. Format code:
   ```bash
   poetry run black .
   ```

## Security

- Never commit your `.env` file or any API keys to version control
- The `.gitignore` is configured to exclude sensitive files
- Use environment variables for all sensitive configuration

## License

MIT License
