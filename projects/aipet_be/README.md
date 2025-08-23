# aipet_be Project

This is a python hexagonal project that is compatible with the hextech monorepo.

This is not intended to be used standalone and is separate to facilitate "copier"s update functionality that relies on using git to create a diff if this template is updated to update existing projects.

## AI Features

This project includes AI-powered pet care recommendations using pydantic_ai and OpenRouter.

### Setup

1. **Get an OpenRouter API Key**: Visit [OpenRouter](https://openrouter.ai/) and create an account
2. **Configure Environment**: Add your API key to `env/local.env`:
   ```bash
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```
3. **Test the Integration**: Run the integration test:
   ```bash
   cd src
   python apps/aipet/tests/test_openrouter_integration.py
   ```

### Usage

The AI agent provides intelligent recommendations for pet care based on current needs:

```python
from apps.aipet.agents.aipet_agent import AipetAgent, PetNeeds

agent = AipetAgent()
pet_needs = PetNeeds(hungry=80, tiredness=30, boredom=60, toilet=20)
recommendations = await agent.get_recommendations(pet_needs)
```

### API Endpoints

- `POST /api/v1/aipet/recommendations` - Get recommendations with structured input
- `POST /api/v1/aipet/recommendations/dict` - Get recommendations with dictionary input

For detailed setup instructions, see [OpenRouter Setup Documentation](docs/OPENROUTER_SETUP.md).

## Testing

The project is configured to run tests in parallel using pytest-xdist for improved performance.

### Running Tests

- **Parallel tests (default)**: `make test` - Automatically detects CPU cores and runs tests in parallel

### Parallel Testing Configuration

- Tests use pytest-xdist with `-n auto` to automatically determine the number of workers
- Each worker process gets its own SQLite database to avoid conflicts
- Coverage data is combined from all worker processes automatically
