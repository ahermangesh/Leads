"""Agent memory and learning system for continuous improvement."""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AgentMemory:
    """Memory system for tracking and learning from agent actions and outcomes."""
    
    def __init__(self, memory_file: str = "data/agent_memory.json"):
        """
        Initialize agent memory.
        
        Args:
            memory_file: Path to memory storage file
        """
        self.memory_file = memory_file
        self.memory = self._load_memory()
        logger.info(f"Agent memory initialized with {len(self.memory.get('campaigns', []))} campaigns")
    
    def _load_memory(self) -> Dict:
        """Load memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                return self._create_empty_memory()
        else:
            return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict:
        """Create empty memory structure."""
        return {
            'campaigns': [],
            'email_performance': {
                'by_strategy': defaultdict(lambda: {'sent': 0, 'opened': 0, 'replied': 0}),
                'by_tone': defaultdict(lambda: {'sent': 0, 'opened': 0, 'replied': 0}),
                'by_industry': defaultdict(lambda: {'sent': 0, 'opened': 0, 'replied': 0})
            },
            'successful_patterns': [],
            'failed_patterns': [],
            'user_preferences': {
                'approved_count': 0,
                'rejected_count': 0,
                'common_edit_reasons': []
            },
            'insights': []
        }
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            logger.info("Memory saved successfully")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def record_campaign(
        self,
        campaign_name: str,
        leads_processed: int,
        emails_sent: int,
        strategy: str,
        tone: str
    ) -> str:
        """
        Record a new campaign.
        
        Args:
            campaign_name: Name of the campaign
            leads_processed: Number of leads processed
            emails_sent: Number of emails sent
            strategy: Email strategy used
            tone: Email tone used
            
        Returns:
            Campaign ID
        """
        campaign = {
            'id': f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': campaign_name,
            'date': datetime.now().isoformat(),
            'leads_processed': leads_processed,
            'emails_sent': emails_sent,
            'strategy': strategy,
            'tone': tone,
            'outcomes': {
                'opened': 0,
                'replied': 0,
                'converted': 0
            }
        }
        
        self.memory['campaigns'].append(campaign)
        self._save_memory()
        
        logger.info(f"Recorded campaign: {campaign_name}")
        return campaign['id']
    
    def record_email_outcome(
        self,
        lead: Dict,
        opened: bool = False,
        replied: bool = False,
        converted: bool = False
    ):
        """
        Record email outcome for learning.
        
        Args:
            lead: Lead dictionary with email details
            opened: Whether email was opened
            replied: Whether lead replied
            converted: Whether lead converted
        """
        strategy = lead.get('email_strategy', 'unknown')
        tone = lead.get('email_tone', 'unknown')
        industry = lead.get('industry', 'unknown')
        
        # Update strategy stats
        if strategy in self.memory['email_performance']['by_strategy']:
            stats = self.memory['email_performance']['by_strategy'][strategy]
        else:
            stats = {'sent': 0, 'opened': 0, 'replied': 0}
            self.memory['email_performance']['by_strategy'][strategy] = stats
        
        stats['sent'] += 1
        if opened:
            stats['opened'] += 1
        if replied:
            stats['replied'] += 1
        
        # Update tone stats
        if tone not in self.memory['email_performance']['by_tone']:
            self.memory['email_performance']['by_tone'][tone] = {'sent': 0, 'opened': 0, 'replied': 0}
        
        tone_stats = self.memory['email_performance']['by_tone'][tone]
        tone_stats['sent'] += 1
        if opened:
            tone_stats['opened'] += 1
        if replied:
            tone_stats['replied'] += 1
        
        # Update industry stats
        if industry not in self.memory['email_performance']['by_industry']:
            self.memory['email_performance']['by_industry'][industry] = {'sent': 0, 'opened': 0, 'replied': 0}
        
        industry_stats = self.memory['email_performance']['by_industry'][industry]
        industry_stats['sent'] += 1
        if opened:
            industry_stats['opened'] += 1
        if replied:
            industry_stats['replied'] += 1
        
        # Record successful patterns
        if replied or converted:
            pattern = {
                'strategy': strategy,
                'tone': tone,
                'industry': industry,
                'quality_score': lead.get('quality_score', 0),
                'had_pain_points': bool(lead.get('pain_points')),
                'outcome': 'replied' if replied else 'converted',
                'recorded_at': datetime.now().isoformat()
            }
            self.memory['successful_patterns'].append(pattern)
        
        self._save_memory()
        logger.info(f"Recorded email outcome for {lead.get('business_name')}")
    
    def record_user_approval(self, lead: Dict, approved: bool, reason: Optional[str] = None):
        """
        Record user approval/rejection for learning preferences.
        
        Args:
            lead: Lead dictionary
            approved: Whether user approved
            reason: Optional reason for rejection
        """
        if approved:
            self.memory['user_preferences']['approved_count'] += 1
        else:
            self.memory['user_preferences']['rejected_count'] += 1
            if reason:
                self.memory['user_preferences']['common_edit_reasons'].append({
                    'reason': reason,
                    'strategy': lead.get('email_strategy'),
                    'tone': lead.get('email_tone'),
                    'date': datetime.now().isoformat()
                })
        
        self._save_memory()
    
    def get_best_strategy(self, industry: Optional[str] = None) -> str:
        """
        Get the best performing email strategy.
        
        Args:
            industry: Optional industry to filter by
            
        Returns:
            Best strategy name
        """
        if industry and industry in self.memory['email_performance']['by_industry']:
            # Industry-specific stats
            stats = self.memory['email_performance']['by_industry'][industry]
            if stats['sent'] > 0:
                reply_rate = stats['replied'] / stats['sent']
                return f"Best for {industry}: {reply_rate:.1%} reply rate"
        
        # Overall best strategy
        best_strategy = 'value_proposition'  # Default
        best_rate = 0.0
        
        for strategy, stats in self.memory['email_performance']['by_strategy'].items():
            if stats['sent'] > 5:  # Minimum sample size
                reply_rate = stats['replied'] / stats['sent']
                if reply_rate > best_rate:
                    best_rate = reply_rate
                    best_strategy = strategy
        
        return best_strategy
    
    def get_best_tone(self) -> str:
        """
        Get the best performing email tone.
        
        Returns:
            Best tone
        """
        best_tone = 'professional'  # Default
        best_rate = 0.0
        
        for tone, stats in self.memory['email_performance']['by_tone'].items():
            if stats['sent'] > 5:
                reply_rate = stats['replied'] / stats['sent']
                if reply_rate > best_rate:
                    best_rate = reply_rate
                    best_tone = tone
        
        return best_tone
    
    def get_performance_summary(self) -> Dict:
        """
        Get overall performance summary.
        
        Returns:
            Performance statistics
        """
        total_sent = sum(
            stats['sent'] 
            for stats in self.memory['email_performance']['by_strategy'].values()
        )
        total_opened = sum(
            stats['opened']
            for stats in self.memory['email_performance']['by_strategy'].values()
        )
        total_replied = sum(
            stats['replied']
            for stats in self.memory['email_performance']['by_strategy'].values()
        )
        
        return {
            'total_campaigns': len(self.memory['campaigns']),
            'total_emails_sent': total_sent,
            'total_opened': total_opened,
            'total_replied': total_replied,
            'open_rate': (total_opened / total_sent * 100) if total_sent > 0 else 0,
            'reply_rate': (total_replied / total_sent * 100) if total_sent > 0 else 0,
            'user_approval_rate': (
                self.memory['user_preferences']['approved_count'] /
                (self.memory['user_preferences']['approved_count'] + 
                 self.memory['user_preferences']['rejected_count']) * 100
            ) if (self.memory['user_preferences']['approved_count'] + 
                  self.memory['user_preferences']['rejected_count']) > 0 else 0
        }
    
    def get_insights(self) -> List[str]:
        """
        Generate insights from memory data.
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Strategy insights
        strategy_stats = self.memory['email_performance']['by_strategy']
        if strategy_stats:
            best_strategy = self.get_best_strategy()
            insights.append(f"Best performing strategy: {best_strategy}")
        
        # Tone insights
        tone_stats = self.memory['email_performance']['by_tone']
        if tone_stats:
            best_tone = self.get_best_tone()
            insights.append(f"Best performing tone: {best_tone}")
        
        # User preference insights
        approval_count = self.memory['user_preferences']['approved_count']
        rejection_count = self.memory['user_preferences']['rejected_count']
        total = approval_count + rejection_count
        
        if total > 10:
            approval_rate = approval_count / total * 100
            if approval_rate > 80:
                insights.append(f"High approval rate ({approval_rate:.1f}%) - agent is well-calibrated")
            elif approval_rate < 50:
                insights.append(f"Low approval rate ({approval_rate:.1f}%) - consider adjusting criteria")
        
        # Success pattern insights
        if len(self.memory['successful_patterns']) > 5:
            industries = [p['industry'] for p in self.memory['successful_patterns']]
            if industries:
                most_common = max(set(industries), key=industries.count)
                insights.append(f"Most successful industry: {most_common}")
        
        return insights
    
    def recommend_improvements(self) -> List[str]:
        """
        Recommend improvements based on memory.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        performance = self.get_performance_summary()
        
        # Reply rate recommendations
        if performance['reply_rate'] < 5 and performance['total_emails_sent'] > 20:
            recommendations.append("Low reply rate - consider more personalized research or different strategies")
        
        # Approval rate recommendations
        if performance['user_approval_rate'] < 60 and performance['total_emails_sent'] > 10:
            recommendations.append("Low user approval rate - agent may need recalibration")
        
        # Strategy diversity
        strategies_used = len([s for s in self.memory['email_performance']['by_strategy'] if self.memory['email_performance']['by_strategy'][s]['sent'] > 0])
        if strategies_used < 2 and performance['total_emails_sent'] > 20:
            recommendations.append("Try testing different email strategies for better results")
        
        return recommendations

# Global instance
agent_memory = AgentMemory()

if __name__ == "__main__":
    # Test memory system
    print("Testing Agent Memory...")
    
    # Test recording a campaign
    campaign_id = agent_memory.record_campaign(
        "Test Campaign",
        leads_processed=10,
        emails_sent=5,
        strategy="value_proposition",
        tone="professional"
    )
    print(f"✓ Recorded campaign: {campaign_id}")
    
    # Test recording outcomes
    test_lead = {
        'business_name': 'Test Business',
        'email_strategy': 'value_proposition',
        'email_tone': 'professional',
        'industry': 'Technology',
        'quality_score': 75
    }
    
    agent_memory.record_email_outcome(test_lead, opened=True, replied=True)
    print("✓ Recorded email outcome")
    
    # Get performance summary
    summary = agent_memory.get_performance_summary()
    print(f"\n Performance Summary:")
    print(f"  Campaigns: {summary['total_campaigns']}")
    print(f"  Emails Sent: {summary['total_emails_sent']}")
    print(f"  Reply Rate: {summary['reply_rate']:.1f}%")
    
    # Get insights
    insights = agent_memory.get_insights()
    if insights:
        print(f"\nInsights:")
        for insight in insights:
            print(f"  - {insight}")
    
    print("\n✓ Memory system working correctly")

