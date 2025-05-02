# Development Rules for Lead Scraper Project

## Code Style & Practices
- Follow PEP8 conventions for Python code (naming, indentation, line length ≤ 79 chars)
- Include docstrings for all functions and classes in Google-style
- Use type hints for all function signatures and class attributes
- Modularize code: each file should expose clear, single-purpose functions or classes

## Error Handling & Logging
- Wrap external calls (HTTP, Selenium) with the retry decorator from utils/helpers.py (max 3 retries, exponential backoff)
- Catch and log all exceptions to a logger configured via helpers.setup_logger at INFO level for normal operations and ERROR for exceptions
- Do not allow uncaught exceptions to crash the entire pipeline; non-fatal errors should be logged and processing should continue

## Resource & Performance Management
- Use Selenium in headless mode with randomized user-agents for all browser automation
- Implement rate limiting for HTTP requests (max 1 request/sec) when scraping websites
- Batch Google Maps results scrolling to minimize repeated DOM queries: scroll 3 times per page load, then parse loaded elements

## Security & Privacy
- Sanitize all user inputs from the UI before using them in URLs or database queries
- Do not hardcode sensitive data or credentials; if proxies or API keys are needed, read from environment variables
- Ensure all HTTP requests use HTTPS endpoints

## Testing & CI
- Write pytest unit tests covering at least 80% of helper functions and scrapers
- Provide fixtures or mocks for external interactions (e.g., HTML pages, Selenium elements) in tests to avoid live calls
- Configure GitHub Actions (or equivalent CI) to run tests on every push and PR, and to lint code using flake8

## Documentation & Comments
- Update README.md after each major feature with usage instructions and examples
- Comment on complex logic blocks explaining the purpose and algorithmic steps
- Maintain the canvas document as the source of truth, updating it whenever architecture or flow changes

## Extensibility & Configuration
- Use a configuration file (e.g., config.yaml) for adjustable parameters: timeouts, max pages, rate limits, user-agents list
- Design scraper modules to implement a common interface (e.g., scrape(keyword, location)) so new platforms can be added seamlessly

## UI/UX
- In the Streamlit UI, display clear progress messages for each module (e.g., "Google Maps: Page 2/5 scraped")
- Disable the Start Scraping button while scraping is in progress to prevent duplicate runs
- Provide error pop-ups or status banners in UI when critical failures occur

## Versioning & Deployment
- Tag releases in Git with semantic versioning (e.g., v1.0.0)
- Include a Dockerfile that sets up a reproducible environment, installs dependencies, and runs the Streamlit app
- Document deployment steps for local, Docker, and cloud environments in DEPLOYMENT.md