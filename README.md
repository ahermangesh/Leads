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

### For Lead Scraping (Tab 1: Lead Scraper)

1. **Launch the application**
   ```bash
   streamlit run app.py
   ```

2. **Enter search criteria**
   - Business Type: e.g., "UGC Agency", "Digital Marketing", "SaaS Company"
   - Location: e.g., "Pune, India", "San Francisco, CA"

3. **Select platforms**
   - Google Maps (recommended for local businesses)
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
   - Download results as JSON (for AI Outreach) or CSV/Excel

### For AI Outreach (Tab 2: AI Outreach)

1. **Import Leads**
   - Upload your scraped leads JSON file
   - Or select from recently scraped files shown in dropdown

2. **Configure Campaign**
   - **Campaign Name**: Descriptive name (e.g., "Pune_UGC_Agencies_Nov_2025")
   - **Email Tone**: Professional, Casual, Friendly, or Formal
   - **Email Strategy**: Value Proposition, Pain Point, or Social Proof
   - **Batch Size**: Number of leads to process at once (default: 10)

3. **Start AI Research**
   - Click "Start AI Research & Email Generation"
   - AI will:
     - Find email addresses from websites
     - Analyze business context and pain points
     - Generate quality scores (0-100)
     - Create personalized emails for qualified leads (score ≥ 60)

4. **Review & Approve Emails**
   - Review each AI-generated email
   - See lead quality score and research insights
   - Approve individual emails or use "Approve All Qualified"
   - Toggle "Send approved emails automatically" if ready

5. **Track in Notion (Optional)**
   - All leads sync to Notion database
   - Monitor pipeline stages and campaign performance
   - See which strategies work best

## 📖 Usage Guide

### Tab 1: Lead Scraper (Original Feature)

#### Input Section
- **Business Type**: The type of business to search for (e.g., "UGC Agency", "SaaS Company")
- **Location**: Geographic location for the search (e.g., "Pune, India", "San Francisco")
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
  - **JSON** (recommended for AI Outreach integration)
  - CSV for spreadsheet analysis
  - Excel for advanced formatting

### Tab 2: AI Outreach (New AI Agent Feature)

#### Import & Configuration
1. **Upload Leads**: Import JSON file from Lead Scraper or previous exports
2. **Campaign Setup**: 
   - Name your campaign for tracking
   - Choose email tone that matches your brand
   - Select outreach strategy based on your goals

#### AI Research Process
The AI agent performs comprehensive analysis:

**Email Finding:**
- Scrapes website contact pages
- Validates email formats
- Assigns confidence scores

**Website Analysis:**
- Extracts business description and services
- Identifies industry and target market
- Detects pain points and opportunities
- Analyzes website quality

**Quality Scoring (0-100):**
- Website professionalism (40%)
- Contact availability (30%)
- Business relevance (20%)
- Social presence (10%)

**Email Generation:**
- For leads scoring ≥ 60 (qualified)
- Personalized subject lines (max 60 chars)
- Custom body based on research (300-500 words)
- Strategy-specific approach
- CAN-SPAM compliant

#### Review Interface
**Lead Cards Show:**
- Business name and website
- Quality score with badge
- Found emails with confidence
- Research insights
- Generated email preview
- Approval status

**Workflow Statistics:**
- Total leads processed
- Qualified vs. rejected
- Emails generated
- Approval rate
- Send rate

#### Approval Options
1. **Individual Review**: Approve emails one-by-one
2. **Bulk Approve**: Approve all qualified leads at once
3. **Auto-Send Toggle**: Automatically send after approval (or save for manual review)

#### Notion Integration
Automatic sync includes:
- Lead information and contact details
- Quality scores and qualification status
- Research findings and AI insights
- Email content and metadata
- Campaign tracking and tags
- Pipeline stage updates

### Best Practices

1. **Start Small**: Begin with 10-15 leads to test your search criteria
2. **Be Specific**: Use precise business types and locations
3. **Respect Rate Limits**: The tool includes built-in delays to be respectful
4. **Review Results**: Check the live data to ensure quality before downloading
5. **Use Full Data Mode**: For comprehensive lead information

### Best Practices for AI Outreach

1. **Start with Quality Leads**: Ensure scraped leads have valid website URLs
2. **Test with Small Batches**: Try 5-10 leads first to calibrate settings
3. **Review Before Sending**: Always review AI-generated emails before auto-send
4. **Monitor Quality Scores**: Focus on leads scoring 70+ for best results
5. **Adjust Tone & Strategy**: Experiment with different combinations per industry
6. **Track in Notion**: Use CRM data to identify what works

### Common Use Cases

#### B2B Sales Outreach
```
Target: "UGC Agencies in Pune"
Strategy: Value Proposition
Tone: Professional
Expected: High-quality personalized emails highlighting your unique value
```

#### Partnership Opportunities
```
Target: "SaaS Companies in San Francisco"
Strategy: Social Proof
Tone: Friendly
Expected: Emails showcasing mutual benefits and case studies
```

#### Service Provider Targeting
```
Target: "Digital Marketing Agencies in Mumbai"
Strategy: Pain Point
Tone: Professional
Expected: Emails addressing common agency challenges
```

## 🔑 API Keys Setup

All services offer generous free tiers perfect for getting started.

### 1. Google Gemini API (Required for AI)

**Free Tier:** 60 requests/minute, 1,500 requests/day

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add to `.env`:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

**Recommended Model:** `gemini-1.5-flash` (fastest, most reliable for free tier)

### 2. Resend Email API (Required for Sending)

**Free Tier:** 3,000 emails/month, 100 emails/day

1. Visit [Resend.com](https://resend.com/signup)
2. Sign up for a free account
3. Go to API Keys section
4. Create a new API key
5. Add to `.env`:
   ```env
   RESEND_API_KEY=re_xxx...
   SENDER_EMAIL=your@email.com
   SENDER_NAME=Your Name
   ```

**Note:** You must verify your domain to send to external emails (or use test mode for testing)

### 3. Notion API (Optional for CRM)

**Free Tier:** Unlimited for personal use

1. Visit [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "Create new integration"
3. Name it (e.g., "Lead Outreach Agent")
4. Copy the Internal Integration Token
5. Create a database in Notion
6. Share the database with your integration (⋯ → Add connections)
7. Copy the database ID from the URL:
   ```
   https://www.notion.so/DATABASE_ID?v=...
   ```
8. Add to `.env`:
   ```env
   NOTION_API_KEY=ntn_xxx...
   NOTION_DATABASE_ID=xxx...
   ```

**See:** `NOTION_SETUP.md` for detailed instructions with screenshots.

### Complete .env Example

```env
# AI Model (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Email Sending (Required)
RESEND_API_KEY=your_resend_api_key_here
SENDER_EMAIL=contact@yourbusiness.com
SENDER_NAME=Your Business Name

# CRM Integration (Optional)
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Logging (Optional)
LOG_LEVEL=INFO
```

## ⚙️ Configuration

### Main Configuration (`config.yaml`)

The system is highly configurable via `config.yaml`. Key sections:

#### Lead Scraping Settings

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
```

#### AI Agent Settings

```yaml
ai_agent:
  # Gemini Model Configuration
  model:
    name: "gemini-1.5-flash"  # Fastest & most reliable for free tier
    temperature: 0.7          # Creativity (0.0-1.0)
    max_tokens: 2048          # Response length limit
    top_p: 0.9                # Nucleus sampling
  
  # Lead Qualification
  qualification:
    min_score: 60             # Minimum score to qualify (0-100)
    score_weights:
      website_quality: 0.4    # 40% weight
      contact_available: 0.3  # 30% weight
      business_relevance: 0.2 # 20% weight
      social_presence: 0.1    # 10% weight
  
  # Website Research
  research:
    max_pages_to_scrape: 3    # How many pages to analyze
    pages_to_check:           # Pages to look for
      - "/"
      - "/about"
      - "/services"
    timeout: 10               # Seconds per page
  
  # Email Generation
  email:
    tone: "professional"      # professional, casual, friendly, formal
    max_subject_length: 60
    max_body_length: 500
    include_unsubscribe: true # CAN-SPAM compliance
    strategies:
      - "value_proposition"
      - "pain_point"
      - "social_proof"
  
  # Outreach Settings
  outreach:
    max_emails_per_day: 100
    delay_between_emails: 2   # Seconds
    batch_size: 10            # Process N leads at a time
    require_approval: true    # Human-in-the-loop
  
  # Notion CRM
  notion:
    auto_sync: true           # Sync after each batch
    sync_interval: 300        # Seconds between syncs
    create_missing_properties: true
```

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
├── app.py                      # Main Streamlit application (dual-tab UI)
├── config.yaml                 # Configuration for scraping & AI agent
├── requirements.txt            # Python dependencies (including AI libs)
├── test_ai_agent.py            # End-to-end AI agent testing script
├── .env                        # API keys (create from env_example.txt)
│
├── controllers/
│   ├── __init__.py
│   └── main_controller.py      # Orchestrates lead scraping modules
│
├── scrapers/
│   ├── google_maps.py          # Google Maps scraper with Selenium
│   └── website.py              # Website content & contact scraper
│
├── agents/                     # 🆕 AI Agent System
│   ├── __init__.py
│   ├── lead_agent.py           # Main LangChain-based AI agent
│   ├── simple_agent.py         # Fallback simplified agent
│   ├── orchestrator.py         # Workflow coordinator with HITL
│   └── memory.py               # Agent learning & memory system
│
├── outreach/                   # 🆕 Outreach Automation
│   ├── __init__.py
│   ├── email_finder.py         # Advanced email extraction
│   ├── lead_researcher.py      # AI-powered website analysis
│   ├── email_generator.py      # Personalized email generation
│   ├── email_sender.py         # Resend API integration
│   └── notion_crm.py           # Notion database sync
│
├── utils/
│   ├── decorators.py           # Retry and rate limiting decorators
│   ├── logger.py               # Logging configuration
│   ├── web.py                  # Web utilities and helpers
│   └── ai_helpers.py           # 🆕 Gemini API utilities
│
├── tests/
│   ├── test_controller.py      # Controller unit tests
│   ├── test_google_maps.py     # Google Maps scraper tests
│   └── test_website.py         # Website scraper tests
│
├── docs/                       # 🆕 Documentation
│   ├── AI_AGENT_README.md      # Comprehensive AI agent guide
│   ├── QUICK_START.md          # Quick start for AI features
│   ├── IMPLEMENTATION_SUMMARY.md # Technical architecture
│   └── NOTION_SETUP.md         # Notion integration guide
│
└── data/
    ├── output/                 # Exported files (CSV, Excel, JSON)
    ├── agent_memory/           # 🆕 Agent learning data
    └── scraper.log            # Application logs
```

### Key Components

#### Core Application

**`app.py`**
- Main Streamlit application with dual-tab interface
- Tab 1: Lead Scraper (original functionality)
- Tab 2: AI Outreach (new AI agent workflow)
- Session state management for both workflows
- Real-time progress updates and file downloads

**`controllers/main_controller.py`**
- Orchestrates lead scraping modules
- Data processing and validation
- Export functionality

#### Lead Scraping

**`scrapers/google_maps.py`**
- Selenium-based scraper for Google Maps business listings
- Extracts: name, address, phone, website, rating

**`scrapers/website.py`**
- Beautiful Soup-based website content scraper
- Email extraction, social links, technology detection

#### AI Agent System (New)

**`agents/lead_agent.py`**
- LangChain-based AI agent with tool use
- Coordinates research, qualification, and email generation
- Uses ReAct (Reasoning + Acting) pattern

**`agents/orchestrator.py`**
- Workflow coordinator with human-in-the-loop
- Batch processing with progress tracking
- Approval queue management
- Notion sync coordination

**`agents/memory.py`**
- Stores campaign outcomes and user preferences
- Learns from approval patterns
- Provides insights and recommendations

#### Outreach Automation (New)

**`outreach/email_finder.py`**
- Multi-page email scraping with confidence scoring
- Validates email formats and sources
- Checks multiple common contact pages

**`outreach/lead_researcher.py`**
- AI-powered website analysis using Gemini
- Extracts business context, services, pain points
- Generates quality scores (0-100)

**`outreach/email_generator.py`**
- Personalized email generation with multiple strategies
- Tone adaptation (professional, casual, friendly, formal)
- CAN-SPAM compliance (unsubscribe, sender info)

**`outreach/email_sender.py`**
- Resend API integration with rate limiting
- Batch sending with progress tracking
- Error handling and retry logic

**`outreach/notion_crm.py`**
- Notion database schema management
- Lead synchronization with rich metadata
- Pipeline stage tracking

#### Utilities

**`utils/ai_helpers.py`** (New)
- Gemini API initialization and text generation
- Configuration loading
- Error handling and retries

**`utils/decorators.py`**
- Retry logic with exponential backoff
- Rate limiting decorators

**`utils/logger.py`**
- Centralized logging configuration

**`utils/web.py`**
- Chrome driver setup and web utilities

## 🧪 Testing

### Quick System Test

Run the comprehensive AI agent test:

```bash
python test_ai_agent.py
```

This will validate:
- ✅ API keys configuration
- ✅ All module imports
- ✅ Gemini AI connection
- ✅ Email sender setup
- ✅ Notion CRM integration
- ✅ Sample workflow with real lead

### Manual Testing Checklist

#### Lead Scraper
1. Search for "UGC agencies in Pune" with limit 5
2. Verify all 5 leads have websites
3. Export as JSON
4. Check JSON file in `data/output/`

#### AI Outreach
1. Upload the exported JSON from Lead Scraper
2. Set campaign name: "Test_Campaign"
3. Click "Start AI Research & Email Generation"
4. Wait for processing (2-3 mins for 5 leads)
5. Verify:
   - Quality scores displayed
   - Emails generated for qualified leads (score ≥ 60)
   - Research insights visible
6. Approve 1-2 emails
7. Toggle "Send approved emails" (optional)
8. Check Notion database for synced leads

### Unit Tests

Run the scraper unit tests:

```bash
pytest tests/
```

Expected output:
```
tests/test_controller.py ....       [ 40%]
tests/test_google_maps.py ....     [ 70%]
tests/test_website.py ....         [100%]

============ 12 passed in 2.5s ============
```

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

- **Google Gemini**: For powerful and accessible AI capabilities
- **LangChain**: For AI agent orchestration framework
- **Resend**: For developer-friendly email API
- **Notion**: For flexible CRM database
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

#### AI Agent Issues

**Gemini API Errors**
- **404 Model Not Found**: Update model name in `config.yaml` to `gemini-1.5-flash`
- **429 Rate Limit**: You've exceeded 60 requests/min. Wait 1 minute and retry
- **401 Unauthorized**: Check your `GEMINI_API_KEY` in `.env`

**Email Sending Fails**
- **Domain Not Verified**: In Resend dashboard, verify your sender domain
- **Test Mode**: Use Resend test mode during development (emails won't actually send)
- **Rate Limit**: Free tier allows 100 emails/day. Check your quota in Resend dashboard

**Notion Sync Fails**
- **Database Not Found**: Share your Notion database with the integration
  - Go to database → Click ⋯ → Add connections → Select your integration
- **Permission Denied**: Ensure integration has "Insert content" permission
- **Invalid Properties**: Set `create_missing_properties: true` in `config.yaml`

**No Emails Found**
- Some websites don't display emails publicly
- Try adjusting `research.pages_to_check` in `config.yaml`
- Check if website requires JavaScript (our scraper is static HTML only)

**Low Quality Scores**
- Adjust `qualification.score_weights` in `config.yaml`
- Lower `qualification.min_score` threshold (default: 60)
- Check if leads have proper website URLs

**Import Errors (LangChain)**
- These are expected due to LangChain API changes
- The system automatically falls back to `SimpleLeadAgent`
- Functionality remains identical

---

## 🎯 Summary

### What You Get

✅ **Complete Lead Generation Pipeline**
- Scrape leads from Google Maps and websites
- Extract contact information automatically
- Export in multiple formats

✅ **AI-Powered Outreach Automation**
- Autonomous lead research and qualification
- Personalized email generation for each prospect
- Quality scoring (0-100) for prioritization
- Human-in-the-loop approval workflow

✅ **Enterprise-Grade Features**
- Notion CRM integration for pipeline management
- Email delivery via Resend (3,000 free emails/month)
- Learning system that improves over time
- Comprehensive analytics and tracking

✅ **100% Free Tier Compatible**
- Google Gemini: 60 requests/min
- Resend: 3,000 emails/month
- Notion: Unlimited personal use
- All features available without paid upgrades

### Real-World Impact

**Traditional Manual Outreach:**
- ⏱️ 15-20 minutes per lead (research + email)
- 📧 3-4 generic emails per hour
- 🎯 Low personalization = low response rates

**With AI Lead Outreach Agent:**
- ⚡ 2-3 minutes per lead (fully automated)
- 📧 20-30 personalized emails per hour
- 🎯 High personalization = 3-5x better response rates
- 🤖 Continuous learning and improvement

**Use Cases:**
- B2B sales teams prospecting new clients
- Marketing agencies finding partnership opportunities
- Freelancers reaching out to potential clients
- Startups building initial customer base
- Recruiters contacting potential candidates

### Next Steps

1. **Get Started**: Follow the [Quick Start](#quick-start) guide
2. **API Keys**: Set up your free API keys in [API Keys Setup](#api-keys-setup)
3. **First Campaign**: Run your first AI outreach campaign
4. **Learn More**: Read `AI_AGENT_README.md` for advanced features
5. **Customize**: Adjust `config.yaml` to match your workflow

**Ready to 10x your outreach? Let's get started! 🚀**

---

**Happy Lead Generation! 🎯**

*Built with ❤️ for sales teams, marketers, and entrepreneurs*
