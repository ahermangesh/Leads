# AI Lead Outreach Agent 🎯

A complete AI-powered lead generation and outreach automation platform. This system doesn't just scrape leads - it autonomously researches businesses, generates personalized outreach emails, and manages your entire outreach workflow with intelligent decision-making powered by Google's Gemini AI.

## 🚀 Features

### 🤖 AI Agent Capabilities (NEW!)
- **Autonomous Research**: AI analyzes websites to understand business context, pain points, and opportunities
- **Intelligent Qualification**: Automatic lead scoring (0-100) based on quality indicators
- **Personalized Email Generation**: Gemini AI writes unique, customized outreach emails for each lead
- **Smart Email Finding**: Multi-page scraping with confidence scoring for contact emails
- **Learning System**: Agent improves over time by tracking outcomes and user preferences
- **Human-in-the-Loop**: Hybrid autonomy with approval workflow for quality control

### 📊 Lead Scraping
- **Multi-Platform Scraping**: Extract leads from Google Maps and websites
- **Contact Extraction**: Automatically collect phone numbers and email addresses
- **Business Intelligence**: Gather business names, addresses, ratings, and social media profiles
- **Real-time Dashboard**: Live updates during scraping with progress tracking
- **Export Options**: Download results in CSV, Excel, or JSON formats

### ✉️ Outreach Automation
- **Email Personalization**: Multiple strategies (value proposition, pain point, social proof)
- **Tone Adaptation**: Professional, casual, friendly, or formal writing styles
- **CAN-SPAM Compliance**: Automatic unsubscribe links and proper sender identification
- **Resend Integration**: Reliable email delivery with rate limiting (3,000 emails/month free)
- **Batch Processing**: Queue and send emails efficiently with progress tracking

### 🗃️ CRM Integration
- **Notion Database**: Complete CRM tracking with rich metadata
- **Pipeline Management**: Track leads through stages (New → Researching → Qualified → Sent → Replied)
- **Analytics**: Monitor open rates, reply rates, and campaign performance
- **Tags & Campaigns**: Organize leads by industry, priority, and campaign

### 🧠 Intelligence & Learning
- **Quality Scoring**: AI evaluates leads based on website quality, contact availability, and relevance
- **Performance Tracking**: Monitors which strategies work best per industry
- **User Preference Learning**: Adapts to your approval patterns over time
- **Insights Generation**: Provides recommendations for improving campaigns

### 💻 User Experience
- **Dual Interface**: Lead Scraper tab + AI Outreach Agent tab
- **Live Progress**: Real-time updates during AI research and email generation
- **Approval Interface**: Review AI-generated emails before sending
- **Statistics Dashboard**: Comprehensive metrics on qualification, approval, and send rates

## 📋 Table of Contents

- [What Makes This an AI Agent?](#what-makes-this-an-ai-agent)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [AI Outreach Workflow](#ai-outreach-workflow)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Keys Setup](#api-keys-setup)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🤖 What Makes This an AI Agent?

This isn't just automation - it's a **true AI agent** that:

1. **Perceives**: Scrapes and analyzes website content to understand business context
2. **Reasons**: Uses Gemini AI to identify pain points, value propositions, and opportunities
3. **Decides**: Autonomously qualifies leads and prioritizes based on quality scoring
4. **Acts**: Generates and executes personalized outreach campaigns
5. **Learns**: Tracks outcomes and improves performance over time

**Key Difference from Traditional Automation:**
- Traditional: Follow rigid scripts → Same email for everyone
- AI Agent: Understand context → Unique strategy per lead → Adapt based on results

## 🛠 Installation

### Prerequisites
- Python 3.9 or higher
- Chrome browser (for Selenium automation)
- Git
- **API Keys** (all free tiers):
  - Google Gemini API (60 requests/min)
  - Resend Email API (3,000 emails/month)
  - Notion API (optional, for CRM tracking)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Leads
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
   
   Rename `env_example.txt` to `.env` and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   RESEND_API_KEY=your_resend_key_here
   NOTION_API_KEY=your_notion_key_here (optional)
   NOTION_DATABASE_ID=your_database_id_here (optional)
   SENDER_EMAIL=your@email.com
   SENDER_NAME=Your Name
   ```

   See [API Keys Setup](#api-keys-setup) for detailed instructions.

5. **Test the system**
   ```bash
   python test_ai_agent.py
   ```

6. **Launch the application**
   ```bash
   streamlit run app.py
   ```

The application will open in your browser at `http://localhost:8501`.

## 🚀 Quick Start

1. **Launch the application**
   ```bash
   streamlit run app.py
   ```

2. **Enter search criteria**
   - Business Type: e.g., "Restaurant", "Cafe", "Dental Clinic"
   - Location: e.g., "New York, NY", "Los Angeles, CA"

3. **Select platforms**
   - Google Maps (recommended)
   - Website Scraper (for email enrichment)

4. **Choose scraping mode**
   - **Contacts Only**: Basic contact information
   - **Full Data**: Includes website analysis and social media links

5. **Set extraction limit**
   - Recommended: 15-50 leads for testing
   - Higher numbers may take longer to process

6. **Start scraping and monitor progress**
   - Watch live data collection
   - View real-time logs
   - Download results when complete

## 📖 Usage Guide

### Interface Overview

#### Input Section
- **Business Type**: The type of business to search for (e.g., "Coffee Shop")
- **Location**: Geographic location for the search (e.g., "Manhattan, New York")
- **Maximum Leads**: Limit the number of results (default: 15)

#### Platform Selection
- **Google Maps**: Primary source for business listings with contact info
- **Website Scraper**: Enriches data with emails and social media links

#### Scraping Modes
- **Contacts Only**: Faster execution, basic contact information
- **Full Data**: Comprehensive analysis including:
  - Email addresses from websites
  - Social media profiles (Instagram, Facebook, LinkedIn)
  - Technology stack detection
  - Additional business insights

#### Results and Export
- **Live Data Table**: See leads as they're collected
- **Detailed View**: Expandable cards with complete information
- **Export Options**: Download in multiple formats
  - CSV for spreadsheet analysis
  - Excel for advanced formatting
  - JSON for data integration

### Best Practices

1. **Start Small**: Begin with 10-15 leads to test your search criteria
2. **Be Specific**: Use precise business types and locations
3. **Respect Rate Limits**: The tool includes built-in delays to be respectful
4. **Review Results**: Check the live data to ensure quality before downloading
5. **Use Full Data Mode**: For comprehensive lead information

### Common Use Cases

#### Sales Prospecting
```
Business Type: "Digital Marketing Agency"
Location: "San Francisco, CA"
Mode: Full Data
Expected Results: Contact info + social media for outreach
```

#### Local Business Research
```
Business Type: "Restaurant"
Location: "Downtown Seattle, WA"
Mode: Contacts Only
Expected Results: Quick list of local restaurants with phone numbers
```

#### Competitor Analysis
```
Business Type: "SaaS Company"
Location: "Austin, TX"
Mode: Full Data
Expected Results: Company details + technology stack information
```

## ⚙️ Configuration

### Main Configuration (`config.yaml`)

```yaml
# Rate Limits (seconds between requests)
rate_limits:
  google_maps: 2
  website_scraper: 1

# Scraping Parameters
max_pages: 5
timeouts:
  page_load: 10
  element_wait: 5
  request: 5

# Browser Settings
selenium:
  headless: true
  user_agents:
    - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."

# Error Handling
retry:
  max_attempts: 3
  initial_delay: 1
  backoff_factor: 2
```

### Environment Variables (Optional)

Create a `.env` file for sensitive configurations:

```env
# Proxy settings (optional)
HTTP_PROXY=http://proxy:8080
HTTPS_PROXY=https://proxy:8080

# Log level
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
Leads/
├── app.py                      # Main Streamlit application
├── config.yaml                # Configuration settings
├── requirements.txt            # Python dependencies
├── DEVELOPMENT_RULES.md        # Development guidelines
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py      # Orchestrates scraping modules
│
├── scrapers/
│   ├── google_maps.py          # Google Maps scraper with Selenium
│   └── website.py              # Website content scraper
│
├── utils/
│   ├── decorators.py           # Retry and rate limiting decorators
│   ├── logger.py               # Logging configuration
│   └── web.py                  # Web utilities and helpers
│
├── tests/
│   ├── test_controller.py      # Controller unit tests
│   ├── test_google_maps.py     # Google Maps scraper tests
│   └── test_website.py         # Website scraper tests
│
└── data/
    ├── output/                 # Exported files (CSV, Excel, JSON)
    └── scraper.log            # Application logs
```

### Key Components

#### `app.py`
- Streamlit user interface
- Real-time progress updates
- File download functionality
- Session state management

#### `controllers/main_controller.py`
- Coordinates all scraping modules
- Input validation and error handling
- Data aggregation and export
- Progress tracking and callbacks

#### `scrapers/google_maps.py`
- Selenium-based Google Maps automation
- Business listing extraction
- Contact information parsing
- Robust element waiting and error handling

#### `scrapers/website.py`
- Website content analysis
- Email extraction using regex patterns
- Social media link detection
- Technology stack identification

#### `utils/`
- **decorators.py**: Retry logic with exponential backoff
- **logger.py**: Centralized logging configuration
- **web.py**: Chrome driver setup and web utilities

## 🧪 Development

### Setting Up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install code quality tools**
   ```bash
   pip install black flake8 mypy pytest pytest-cov
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Code Style Guidelines

- **PEP 8**: Follow Python naming conventions
- **Line Length**: Maximum 79 characters
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Google-style docstrings for all public functions
- **Import Organization**: Standard library, third-party, local imports

### Adding New Scrapers

To add a new platform scraper:

1. **Create scraper module**
   ```python
   # scrapers/new_platform.py
   def scrape(keyword: str, location: str, max_leads: int = 15) -> List[Dict]:
       """
       Scrape leads from new platform.
       
       Args:
           keyword: Business type to search for
           location: Geographic location
           max_leads: Maximum number of leads to extract
           
       Returns:
           List of lead dictionaries
       """
       # Implementation here
       pass
   ```

2. **Update controller**
   ```python
   # controllers/main_controller.py
   from scrapers.new_platform import scrape as scrape_new_platform
   
   # Add to platform mapping
   platform_map = {
       "Google Maps": scrape_maps,
       "Website Scraper": enrich_leads,
       "New Platform": scrape_new_platform,  # Add here
   }
   ```

3. **Add to UI options**
   ```python
   # app.py
   platforms = st.multiselect(
       "Select Platforms",
       ["Google Maps", "Website Scraper", "New Platform"],  # Add here
       default=["Google Maps"]
   )
   ```

### Performance Optimization

- **Rate Limiting**: Respect website terms of service
- **Parallel Processing**: Use threading for I/O-bound operations
- **Caching**: Cache results for repeated searches
- **Memory Management**: Process data in chunks for large datasets

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_google_maps.py

# Run with verbose output
pytest -v
```

### Test Structure

#### Unit Tests
- **test_controller.py**: Controller logic and validation
- **test_google_maps.py**: Google Maps scraper functionality
- **test_website.py**: Website scraper and data extraction

#### Integration Tests
- End-to-end scraping workflows
- UI component interactions
- Data export and file generation

#### Test Coverage Goals
- Minimum 80% code coverage
- All critical paths tested
- Error handling scenarios covered

### Writing Tests

```python
# Example test structure
import pytest
from unittest.mock import Mock, patch
from scrapers.google_maps import scrape

def test_google_maps_scrape():
    """Test Google Maps scraping functionality."""
    # Mock Selenium components
    with patch('scrapers.google_maps.webdriver.Chrome') as mock_driver:
        # Setup mocks
        mock_driver.return_value.find_element.return_value.text = "Test Business"
        
        # Execute test
        results = scrape("restaurant", "New York", max_leads=5)
        
        # Assertions
        assert len(results) > 0
        assert "business_name" in results[0]
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   pytest
   flake8 .
   mypy .
   ```

5. **Submit a pull request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for UI changes

### Development Rules

Please read `DEVELOPMENT_RULES.md` for detailed guidelines on:
- Code style and practices
- Error handling and logging
- Resource and performance management
- Security and privacy considerations
- Testing requirements

### Issue Reporting

When reporting issues, please include:
- Python version and operating system
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs
- Screenshots if applicable

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the excellent web framework
- **Selenium**: For robust browser automation
- **BeautifulSoup**: For HTML parsing capabilities
- **Pandas**: For data manipulation and export

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section below
2. Search existing issues on GitHub
3. Create a new issue with detailed information
4. For urgent matters, check the logs in `data/scraper.log`

### Troubleshooting

#### Common Issues

**Chrome Driver Issues**
```bash
# The webdriver-manager will auto-download Chrome driver
# If issues persist, manually update Chrome browser
```

**Permission Errors on Windows**
```bash
# Run terminal as administrator
# Or adjust file permissions for the data/ directory
```

**Memory Issues with Large Datasets**
```bash
# Reduce max_leads parameter
# Monitor memory usage during scraping
```

**Rate Limiting or Blocks**
```bash
# Increase delays in config.yaml
# Use different user agents
# Consider using proxies for large-scale scraping
```

---

**Happy Lead Generation! 🎯**
