# AI Lead Outreach Agent - Quick Start Guide

## 🎯 Welcome!

You now have a fully functional AI agent that can autonomously research leads and generate personalized outreach emails. Here's how to get started in 5 minutes.

## Step 1: Get Your API Keys (FREE)

### Google Gemini AI (Required)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key

### Resend Email (Required for sending)
1. Go to: https://resend.com/signup
2. Create account (free, credit card required but not charged)
3. Verify your sender email
4. Get API key from dashboard

### Notion (Optional - for CRM)
1. Go to: https://www.notion.so/my-integrations
2. Click "+ New integration"
3. Give it a name and copy the API key
4. Create a new page in Notion
5. Share it with your integration
6. Copy the database ID from the URL

## Step 2: Configure the System

1. **Rename `env_example.txt` to `.env`**

2. **Add your API keys to `.env`:**
```env
GEMINI_API_KEY=your_gemini_key_here
RESEND_API_KEY=your_resend_key_here
SENDER_EMAIL=your@verified-email.com
SENDER_NAME=Your Name

# Optional
NOTION_API_KEY=your_notion_key_here
NOTION_DATABASE_ID=your_database_id_here
```

3. **Save the file**

## Step 3: Test the System

Run the test script to verify everything works:

```bash
python test_ai_agent.py
```

You should see:
- ✓ Configuration: PASS
- ✓ Imports: PASS
- ✓ AI Connection: PASS
- ✓ Email Sender: PASS

## Step 4: Run the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Step 5: Your First AI Outreach Campaign

### In the Streamlit App:

1. **Go to the "AI Outreach" tab** (second tab)

2. **Import your leads:**
   - You already have sample data: `leads_UGC agencies_pune_20251105_172006.json`
   - Click "Load Selected" to import these 9 leads

3. **Configure the workflow:**
   - Auto-approve threshold: 80 (only high-quality leads)
   - Send immediately: ✗ (leave unchecked for safety)
   - Sync to Notion: ✓ (if configured)

4. **Click "🚀 Run AI Workflow"**
   - This will take 10-20 minutes for 9 leads
   - Watch the progress in real-time
   - AI will:
     - Find email addresses
     - Research each business
     - Analyze pain points
     - Generate personalized emails
     - Score lead quality

5. **Review the results:**
   - Check "Workflow Statistics"
   - See how many leads qualified
   - Review quality scores

6. **Approve emails:**
   - Click "Awaiting Approval" filter
   - Expand each lead to see:
     - AI research summary
     - Pain points identified
     - Generated email
   - Click "✅ Approve" for good emails
   - Click "❌ Reject" for any you don't like

7. **Send (when ready):**
   - For now, just review - don't send yet
   - In production, you'd configure sending settings
   - Approved emails can be sent in batches

## What Just Happened?

The AI agent:
1. ✅ Visited each business website
2. ✅ Found contact email addresses
3. ✅ Analyzed the business using Gemini AI
4. ✅ Identified pain points and opportunities
5. ✅ Generated personalized emails
6. ✅ Scored each lead (0-100)
7. ✅ Synced everything to Notion (if configured)

## Understanding the Results

### Quality Scores
- **80-100**: Excellent - Safe to auto-approve
- **60-79**: Good - Review recommended
- **40-59**: Fair - Might need manual work
- **0-39**: Poor - Probably not worth pursuing

### Email Strategies
- **Value Proposition**: Focuses on benefits
- **Pain Point**: Addresses specific challenges
- **Social Proof**: Mentions success stories

## Next Steps

### Option A: Test with Real Campaign
1. Scrape new leads (use Lead Scraper tab)
2. Run AI workflow
3. Review and approve emails
4. Send to qualified leads
5. Track responses in Notion

### Option B: Customize the Agent
1. Edit `config.yaml` to adjust:
   - Quality score weights
   - Email tone (professional, casual, etc.)
   - Rate limits
2. Modify email templates in `outreach/email_generator.py`
3. Add custom research criteria in `outreach/lead_researcher.py`

### Option C: Scale Up
1. Get more leads (50-100)
2. Set auto-approve threshold: 80+
3. Enable immediate sending (after testing)
4. Monitor performance in agent memory
5. Let the AI learn and improve

## Pro Tips

### For Best Results:
1. **Start small**: Test with 5-10 leads first
2. **Review manually**: Check first few AI outputs
3. **Provide feedback**: Approve/reject to train the agent
4. **Monitor metrics**: Check agent memory for insights
5. **Be patient**: AI quality improves over time

### Common Mistakes to Avoid:
- ❌ Sending without reviewing first
- ❌ Setting auto-approve too low (<70)
- ❌ Ignoring quality scores
- ❌ Not testing email deliverability
- ❌ Sending too many too fast

## Troubleshooting

### "Gemini API not configured"
- Check `.env` file has correct key
- Verify key at makersuite.google.com
- Make sure no extra spaces in key

### "No emails found"
- Some businesses hide emails
- AI tries multiple pages
- Consider manual lookup for high-value leads

### "Low approval rate"
- Lower quality score threshold
- Adjust email tone in config
- Review AI insights - might be off

### Need Help?
1. Check logs: `data/scraper.log`
2. Run test: `python test_ai_agent.py`
3. Read full guide: `AI_AGENT_README.md`

## Cost Breakdown

Everything is **FREE** to start:

- ✅ **Gemini AI**: Free (60 requests/min)
- ✅ **Resend**: Free (100 emails/day)
- ✅ **Notion**: Free (unlimited pages)
- ✅ **Total**: $0/month for ~100 leads/day

Only cost: Your time reviewing AI output!

## Success Checklist

After your first campaign, you should have:
- ✅ Researched leads with AI insights
- ✅ Quality scores for prioritization
- ✅ Personalized emails generated
- ✅ Leads tracked in Notion
- ✅ Agent learning from your approvals

## What Makes This Special?

This isn't just automation - it's a **true AI agent** that:
1. **Thinks**: Analyzes and understands businesses
2. **Decides**: Qualifies leads autonomously
3. **Creates**: Writes unique, personalized content
4. **Learns**: Improves from your feedback
5. **Acts**: Executes the entire workflow

## Ready to Go?

You're all set! Your AI agent is ready to:
- Research hundreds of leads automatically
- Generate personalized outreach at scale
- Learn your preferences over time
- Save you hours of manual work

Run `streamlit run app.py` and start your first campaign!

---

**Questions?** Read the full guide in `AI_AGENT_README.md`

**Problems?** Check `IMPLEMENTATION_SUMMARY.md` for details

**Happy Lead Generation! 🚀**

