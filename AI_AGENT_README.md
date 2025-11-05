# AI Lead Outreach Agent - User Guide

## Overview

This AI-powered lead outreach system transforms raw lead data into qualified prospects with personalized outreach emails. Using Google's Gemini AI, the system autonomously researches businesses, generates personalized emails, and manages the entire outreach workflow with human oversight.

## What Makes This an AI Agent?

Unlike traditional automation, this system:

1. **Autonomous Decision Making**: AI decides which leads to prioritize based on quality scoring
2. **Intelligent Research**: Analyzes websites to understand business context, pain points, and opportunities
3. **Creative Generation**: Writes unique, personalized emails for each lead based on research
4. **Adaptive Learning**: Learns from outcomes to improve future performance
5. **Goal-Oriented**: Works toward the objective of generating qualified leads with minimal human input

## Features

### 🤖 AI-Powered Research
- Scrapes and analyzes business websites
- Identifies pain points and business needs
- Detects technology stack and industry
- Generates quality scores (0-100) for lead qualification

### ✉️ Intelligent Email Generation
- Personalized subject lines and body content
- Multiple strategies: value proposition, pain point, social proof
- Tone adaptation: professional, casual, friendly, formal
- CAN-SPAM compliant with unsubscribe links

### 🔄 Complete Workflow Automation
- Email address discovery from multiple pages
- Batch processing with rate limiting
- Human-in-the-loop approval system
- Notion CRM integration for tracking

### 📊 Learning & Improvement
- Tracks email performance by strategy, tone, and industry
- Learns user approval patterns
- Provides insights and recommendations
- Continuous improvement over time

## Setup Instructions

### 1. Install Dependencies

```bash
pip install google-generativeai langchain langchain-google-genai resend notion-client validators
```

### 2. Configure API Keys

Rename `env_example.txt` to `.env` and add your API keys:

```env
# Google Gemini API (FREE - 60 requests/min)
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_key_here

# Resend Email API (FREE - 3,000 emails/month)
# Get from: https://resend.com/api-keys
RESEND_API_KEY=your_key_here

# Notion API (FREE personal workspace)
# Get from: https://www.notion.so/my-integrations
NOTION_API_KEY=your_key_here
NOTION_DATABASE_ID=your_database_id_here

# Your verified sender email
SENDER_EMAIL=your@email.com
SENDER_NAME=Your Name
```

### 3. Set Up Notion Database (Optional)

1. Create a new integration at notion.so/my-integrations
2. Create a new database page in Notion
3. Share the database with your integration
4. Copy the database ID from the URL

### 4. Configure Settings

Edit `config.yaml` to customize:

```yaml
ai_agent:
  # AI Model Settings
  model:
    temperature: 0.7
    max_tokens: 2048
  
  # Lead Qualification
  qualification:
    min_score: 60  # Minimum quality score
  
  # Email Settings
  email:
    tone: "professional"
    strategies:
      - "value_proposition"
      - "pain_point"
      - "social_proof"
  
  # Rate Limits
  outreach:
    max_emails_per_day: 50
    delay_between_emails: 10
```

## How to Use

### Method 1: Streamlit UI (Recommended)

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Navigate to "AI Outreach" tab**

3. **Import Leads**
   - Upload JSON file from previous scraping
   - Or select from recent scrapes

4. **Configure Workflow**
   - Set auto-approve threshold (e.g., 80 for high-quality leads)
   - Choose whether to send immediately or review first
   - Enable/disable Notion sync

5. **Run AI Workflow**
   - Click "Run AI Workflow"
   - Monitor progress in real-time
   - Review statistics and logs

6. **Review & Approve Emails**
   - Filter by status (Awaiting Approval, Qualified, etc.)
   - Review AI-generated emails
   - Approve, reject, or edit each email
   - Send approved emails

### Method 2: Command Line

```bash
# Run complete workflow
python agents/orchestrator.py data/output/your_leads.json

# Test individual components
python outreach/email_finder.py https://example.com
python outreach/lead_researcher.py https://example.com "Business Name"
python outreach/email_generator.py data/output/your_leads.json
```

## Workflow Stages

### Stage 1: Lead Import
- Load leads from JSON export
- Initial data validation

### Stage 2: AI Research
1. **Email Discovery**
   - Scans homepage, contact, about pages
   - Validates email addresses
   - Confidence scoring

2. **Business Analysis**
   - AI reads website content
   - Identifies business model and services
   - Detects pain points and opportunities
   - Generates quality score

### Stage 3: Email Generation
1. **Qualification Filter**
   - Only qualified leads (score ≥ threshold)
   - Ensures contact information available

2. **Personalization**
   - AI analyzes research data
   - Generates unique subject line
   - Writes personalized email body
   - Adapts tone and strategy

### Stage 4: Human Review (Hybrid Mode)
- Review AI-generated emails
- Approve, reject, or edit
- Bulk actions for high-quality leads

### Stage 5: Sending
- Respects rate limits
- Tracks send status
- Updates Notion CRM

### Stage 6: Learning
- Records outcomes
- Tracks performance
- Generates insights
- Improves future campaigns

## Understanding Quality Scores

Leads are scored 0-100 based on:

- **Website Quality (30%)**: Has website, successfully analyzed, clear value prop
- **Info Completeness (20%)**: Phone, address, rating available
- **Contact Availability (20%)**: Email found, high confidence
- **Relevance (30%)**: Pain points identified, outreach angles clear, no red flags

**Score Ranges:**
- 80-100: Excellent - Auto-approve candidate
- 60-79: Good - Review recommended
- 40-59: Fair - May need manual research
- 0-39: Poor - Likely not qualified

## Email Strategies

### Value Proposition
- Focuses on benefits you can provide
- Results-oriented messaging
- Best for: Services, B2B solutions

### Pain Point
- Addresses specific challenges
- Empathetic approach
- Best for: Problem-solving services

### Social Proof
- Mentions success with similar businesses
- Credibility-building
- Best for: New markets, competitive industries

## Best Practices

### 1. Start Small
- Test with 5-10 leads first
- Verify AI quality before scaling
- Adjust settings based on results

### 2. Monitor Quality Scores
- Review leads in 60-80 range manually
- Set auto-approve threshold conservatively (80+)
- Reject low-quality leads to improve learning

### 3. Respect Rate Limits
- Stay within free tier limits
- Don't send more than 50 emails/day initially
- Maintain delays between sends

### 4. Review AI Output
- Always review first few emails from each campaign
- Provide feedback through approvals/rejections
- Edit emails to teach the AI your preferences

### 5. Track Performance
- Monitor open and reply rates
- Use Notion to track conversations
- Review agent insights regularly

## Troubleshooting

### "Gemini API not configured"
- Check that GEMINI_API_KEY is set in .env
- Verify key at makersuite.google.com
- Ensure key has no extra spaces

### "No emails found for leads"
- Some businesses don't list emails publicly
- Check if websites are accessible
- Consider manual research for high-value leads

### "Email generation failed"
- Check API quota (60 requests/min for Gemini)
- Verify internet connection
- Review logs in data/scraper.log

### "Low approval rate"
- Lower min_score threshold in config
- Adjust email tone setting
- Review rejection patterns in agent memory

### "Emails not sending"
- Verify RESEND_API_KEY and SENDER_EMAIL
- Check daily send limit not exceeded
- Ensure sender email is verified in Resend

## API Usage & Costs

All services used are **FREE TIER**:

### Google Gemini
- **Free**: 60 requests/minute
- Enough for: ~50 leads/hour
- No credit card required

### Resend
- **Free**: 3,000 emails/month (100/day)
- Enough for: 100 leads/day
- Credit card required (not charged)

### Notion
- **Free**: Unlimited pages on personal plan
- No limits on API calls
- No credit card required

### Estimated Processing Time
- Email finding: ~10-15 seconds/lead
- AI research: ~20-30 seconds/lead
- Email generation: ~10-15 seconds/lead
- **Total**: ~1-2 minutes per lead

## Safety & Compliance

### CAN-SPAM Compliance
- ✅ Unsubscribe link in every email
- ✅ Valid sender information
- ✅ Accurate subject lines
- ✅ Identifies message as advertisement (configurable)

### Rate Limiting
- ✅ Respects API quotas
- ✅ Delays between emails
- ✅ Daily send limits
- ✅ Gradual warmup recommended

### Privacy
- ✅ Only scrapes public information
- ✅ No sensitive data storage
- ✅ GDPR-compliant data handling

## Advanced Features

### Custom Email Templates
Edit `outreach/email_generator.py` to customize prompts and templates.

### Custom Research Criteria
Modify `outreach/lead_researcher.py` to add industry-specific research.

### Notion Database Schema
Customize fields in `outreach/notion_crm.py` for your CRM needs.

### Agent Memory
View and analyze agent learning in `data/agent_memory.json`.

## Performance Optimization

### For Faster Processing
- Reduce `max_pages_to_scrape` in config (default: 3)
- Lower research depth for less critical leads
- Batch process during off-hours

### For Better Quality
- Increase AI temperature for more creative emails (0.7-0.9)
- Add industry-specific research criteria
- Manually enrich high-value leads

### For Higher Volume
- Use multiple sender emails (within limits)
- Stagger campaigns across days
- Consider upgrading to paid tiers

## Support & Feedback

### Check Logs
```bash
tail -f data/scraper.log
```

### Test Components
```bash
# Test AI connectivity
python utils/ai_helpers.py

# Test email sender
python outreach/email_sender.py

# Test Notion sync
python outreach/notion_crm.py
```

### Review Agent Memory
```bash
# View performance
python agents/memory.py
```

## What's Next?

### Phase 1 (Current)
- ✅ AI research and email generation
- ✅ Human-in-the-loop workflow
- ✅ Notion CRM integration
- ✅ Learning system

### Phase 2 (Future)
- 🔄 Automated follow-up sequences
- 🔄 Response handling and categorization
- 🔄 A/B testing framework
- 🔄 Multi-channel outreach (LinkedIn, etc.)

### Phase 3 (Future)
- 🔄 Advanced analytics dashboard
- 🔄 Predictive lead scoring
- 🔄 Conversation intelligence
- 🔄 Full autonomous mode

## Credits

Built with:
- Google Gemini AI for intelligence
- LangChain for agent orchestration
- Streamlit for beautiful UI
- Resend for reliable email delivery
- Notion for CRM tracking

---

**Happy Lead Generation! 🎯**

For questions or issues, check the logs in `data/scraper.log` or review the configuration in `config.yaml`.

