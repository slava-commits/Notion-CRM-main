#!/usr/bin/env python3
"""
Daily Brief Generator
Generates automated daily briefs with action items and communication drafts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class DailyBriefGenerator:
    """Generates daily briefs with AI-powered insights and action items"""
    
    def __init__(self, notion_client):
        self.notion_client = notion_client
        self.ai_client = None  # Will be initialized with AI service
    
    async def generate_brief(self, date: Optional[datetime] = None) -> Optional[str]:
        """Generate daily brief for specified date (defaults to today)"""
        try:
            if date is None:
                date = datetime.now()
            
            logger.info(f"Generating daily brief for {date.date()}")
            
            # Gather data for brief
            brief_data = await self._gather_brief_data(date)
            
            # Generate AI summary
            summary = await self._generate_ai_summary(brief_data)
            
            # Generate action items
            action_items = await self._generate_action_items(brief_data)
            
            # Generate communication drafts
            drafts = await self._generate_communication_drafts(brief_data)
            
            # Create brief in Notion
            brief_id = await self._create_brief_in_notion(date, summary, action_items, drafts)
            
            logger.info(f"Daily brief generated successfully: {brief_id}")
            return brief_id
            
        except Exception as e:
            logger.error(f"Failed to generate daily brief: {e}")
            return None
    
    async def _gather_brief_data(self, date: datetime) -> Dict[str, Any]:
        """Gather all data needed for the brief"""
        try:
            # Get date range for queries
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get waiting on tasks (no reply in N days)
            waiting_tasks = await self._get_waiting_tasks()
            
            # Get due today tasks
            due_today_tasks = await self._get_due_today_tasks(date)
            
            # Get recent interactions
            recent_interactions = await self._get_recent_interactions(hours=24)
            
            # Get social activity
            social_activity = await self._get_recent_social_activity(hours=24)
            
            # Get overdue tasks
            overdue_tasks = await self._get_overdue_tasks()
            
            # Get high-priority contacts
            high_priority_contacts = await self._get_high_priority_contacts()
            
            return {
                'date': date,
                'waiting_tasks': waiting_tasks,
                'due_today_tasks': due_today_tasks,
                'recent_interactions': recent_interactions,
                'social_activity': social_activity,
                'overdue_tasks': overdue_tasks,
                'high_priority_contacts': high_priority_contacts
            }
            
        except Exception as e:
            logger.error(f"Failed to gather brief data: {e}")
            return {}
    
    async def _get_waiting_tasks(self, days_threshold: int = 3) -> List[Dict]:
        """Get tasks waiting on replies"""
        try:
            # Get tasks with "Waiting on reply" reason
            waiting_tasks = await self.notion_client.get_tasks()
            
            # Filter for tasks waiting on replies
            filtered_tasks = []
            for task in waiting_tasks:
                if (task.get('reason') == 'Waiting on reply' and 
                    task.get('status') in ['Todo', 'Doing']):
                    
                    # Check if it's been more than threshold days
                    created_time = task.get('created_time', '')
                    if created_time:
                        created_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        days_since_created = (datetime.now() - created_date).days
                        
                        if days_since_created >= days_threshold:
                            filtered_tasks.append(task)
            
            return filtered_tasks
            
        except Exception as e:
            logger.error(f"Failed to get waiting tasks: {e}")
            return []
    
    async def _get_due_today_tasks(self, date: datetime) -> List[Dict]:
        """Get tasks due today"""
        try:
            all_tasks = await self.notion_client.get_tasks()
            
            due_today = []
            for task in all_tasks:
                due_date = task.get('due_date', '')
                if due_date:
                    task_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                    if task_due_date == date.date() and task.get('status') != 'Done':
                        due_today.append(task)
            
            return due_today
            
        except Exception as e:
            logger.error(f"Failed to get due today tasks: {e}")
            return []
    
    async def _get_recent_interactions(self, hours: int = 24) -> List[Dict]:
        """Get recent interactions"""
        try:
            return await self.notion_client.get_interactions(hours_back=hours)
        except Exception as e:
            logger.error(f"Failed to get recent interactions: {e}")
            return []
    
    async def _get_recent_social_activity(self, hours: int = 24) -> List[Dict]:
        """Get recent social activity"""
        try:
            # Query social activity database
            since_time = datetime.now() - timedelta(hours=hours)
            filter_data = {
                "property": "Timestamp",
                "created_time": {"after": since_time.isoformat()}
            }
            
            return await self.notion_client.query_database(
                self.notion_client.db_ids["social_activity"], 
                filter_data
            )
            
        except Exception as e:
            logger.error(f"Failed to get recent social activity: {e}")
            return []
    
    async def _get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks"""
        try:
            all_tasks = await self.notion_client.get_tasks()
            
            overdue = []
            now = datetime.now()
            
            for task in all_tasks:
                due_date = task.get('due_date', '')
                if due_date and task.get('status') != 'Done':
                    task_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if task_due_date < now:
                        overdue.append(task)
            
            return overdue
            
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {e}")
            return []
    
    async def _get_high_priority_contacts(self) -> List[Dict]:
        """Get high-priority contacts (Tier A)"""
        try:
            filter_data = {
                "property": "Tier",
                "select": {"equals": "A"}
            }
            
            return await self.notion_client.query_database(
                self.notion_client.db_ids["people"], 
                filter_data
            )
            
        except Exception as e:
            logger.error(f"Failed to get high-priority contacts: {e}")
            return []
    
    async def _generate_ai_summary(self, brief_data: Dict[str, Any]) -> str:
        """Generate AI-powered summary of the day's activities"""
        try:
            # Prepare data for AI analysis
            summary_data = {
                'date': brief_data['date'].isoformat(),
                'waiting_count': len(brief_data.get('waiting_tasks', [])),
                'due_today_count': len(brief_data.get('due_today_tasks', [])),
                'overdue_count': len(brief_data.get('overdue_tasks', [])),
                'recent_interactions_count': len(brief_data.get('recent_interactions', [])),
                'social_activity_count': len(brief_data.get('social_activity', [])),
                'high_priority_contacts_count': len(brief_data.get('high_priority_contacts', []))
            }
            
            # Generate summary using AI (placeholder implementation)
            summary = await self._call_ai_service(
                "daily_summary",
                f"Generate a daily brief summary based on this data: {json.dumps(summary_data)}"
            )
            
            return summary or self._generate_fallback_summary(summary_data)
            
        except Exception as e:
            logger.error(f"Failed to generate AI summary: {e}")
            return self._generate_fallback_summary(brief_data)
    
    def _generate_fallback_summary(self, brief_data: Dict[str, Any]) -> str:
        """Generate fallback summary without AI"""
        waiting_count = len(brief_data.get('waiting_tasks', []))
        due_count = len(brief_data.get('due_today_tasks', []))
        overdue_count = len(brief_data.get('overdue_tasks', []))
        interactions_count = len(brief_data.get('recent_interactions', []))
        social_count = len(brief_data.get('social_activity', []))
        
        summary = f"Daily Brief Summary:\n\n"
        summary += f"• {waiting_count} tasks waiting on replies\n"
        summary += f"• {due_count} tasks due today\n"
        summary += f"• {overdue_count} overdue tasks\n"
        summary += f"• {interactions_count} recent interactions\n"
        summary += f"• {social_count} social media activities\n\n"
        
        if overdue_count > 0:
            summary += "⚠️ Attention needed: You have overdue tasks that require immediate action.\n\n"
        
        if waiting_count > 3:
            summary += "📧 Consider following up on pending communications.\n\n"
        
        summary += "Focus on high-priority contacts and urgent tasks today."
        
        return summary
    
    async def _generate_action_items(self, brief_data: Dict[str, Any]) -> List[Dict]:
        """Generate actionable items for the day"""
        action_items = []
        
        try:
            # Add waiting tasks as action items
            for task in brief_data.get('waiting_tasks', []):
                action_items.append({
                    'type': 'follow_up',
                    'title': f"Follow up on: {task.get('title', 'Untitled task')}",
                    'description': f"Waiting on reply for {task.get('reason', 'unknown reason')}",
                    'priority': 'high',
                    'task_id': task.get('id', ''),
                    'person_id': task.get('person_id', ''),
                    'company_id': task.get('company_id', '')
                })
            
            # Add due today tasks
            for task in brief_data.get('due_today_tasks', []):
                action_items.append({
                    'type': 'due_today',
                    'title': f"Complete: {task.get('title', 'Untitled task')}",
                    'description': f"Task due today - {task.get('reason', 'no reason specified')}",
                    'priority': 'high',
                    'task_id': task.get('id', ''),
                    'person_id': task.get('person_id', ''),
                    'company_id': task.get('company_id', '')
                })
            
            # Add overdue tasks
            for task in brief_data.get('overdue_tasks', []):
                action_items.append({
                    'type': 'overdue',
                    'title': f"URGENT: {task.get('title', 'Untitled task')}",
                    'description': f"Overdue task - {task.get('reason', 'no reason specified')}",
                    'priority': 'urgent',
                    'task_id': task.get('id', ''),
                    'person_id': task.get('person_id', ''),
                    'company_id': task.get('company_id', '')
                })
            
            # Generate social engagement actions
            for activity in brief_data.get('social_activity', []):
                if activity.get('action_suggestion'):
                    action_items.append({
                        'type': 'social_engagement',
                        'title': f"Engage with {activity.get('person_name', 'contact')} on {activity.get('network', 'social media')}",
                        'description': activity.get('action_suggestion', ''),
                        'priority': 'medium',
                        'social_activity_id': activity.get('id', ''),
                        'person_id': activity.get('person_id', ''),
                        'company_id': activity.get('company_id', '')
                    })
            
            return action_items
            
        except Exception as e:
            logger.error(f"Failed to generate action items: {e}")
            return []
    
    async def _generate_communication_drafts(self, brief_data: Dict[str, Any]) -> List[Dict]:
        """Generate communication drafts for the day"""
        drafts = []
        
        try:
            # Generate follow-up email drafts for waiting tasks
            for task in brief_data.get('waiting_tasks', []):
                if task.get('person_id'):
                    draft = await self._generate_follow_up_draft(task)
                    if draft:
                        drafts.append(draft)
            
            # Generate social engagement drafts
            for activity in brief_data.get('social_activity', []):
                if activity.get('action_suggestion') and 'congratulate' in activity.get('action_suggestion', '').lower():
                    draft = await self._generate_social_draft(activity)
                    if draft:
                        drafts.append(draft)
            
            return drafts
            
        except Exception as e:
            logger.error(f"Failed to generate communication drafts: {e}")
            return []
    
    async def _generate_follow_up_draft(self, task: Dict) -> Optional[Dict]:
        """Generate follow-up email draft for a task"""
        try:
            person_id = task.get('person_id', '')
            task_title = task.get('title', '')
            reason = task.get('reason', '')
            
            # Get person details
            person_data = await self._get_person_details(person_id)
            if not person_data:
                return None
            
            # Generate draft using AI
            prompt = f"""
            Generate a professional follow-up email for:
            - Person: {person_data.get('name', 'Contact')}
            - Company: {person_data.get('company', 'their company')}
            - Task: {task_title}
            - Reason: {reason}
            
            Make it polite, professional, and actionable.
            """
            
            draft_content = await self._call_ai_service("email_draft", prompt)
            
            if draft_content:
                return {
                    'type': 'email',
                    'recipient': person_data.get('name', ''),
                    'recipient_email': person_data.get('primary_email', ''),
                    'subject': f"Follow-up: {task_title}",
                    'content': draft_content,
                    'task_id': task.get('id', ''),
                    'person_id': person_id
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate follow-up draft: {e}")
            return None
    
    async def _generate_social_draft(self, activity: Dict) -> Optional[Dict]:
        """Generate social media engagement draft"""
        try:
            network = activity.get('network', '')
            person_name = activity.get('person_name', '')
            content = activity.get('content', '')
            action_suggestion = activity.get('action_suggestion', '')
            
            # Generate draft using AI
            prompt = f"""
            Generate a {network} engagement message for:
            - Person: {person_name}
            - Content: {content[:200]}...
            - Action: {action_suggestion}
            
            Make it authentic, engaging, and appropriate for {network}.
            """
            
            draft_content = await self._call_ai_service("social_draft", prompt)
            
            if draft_content:
                return {
                    'type': 'social',
                    'network': network,
                    'recipient': person_name,
                    'content': draft_content,
                    'original_content': content,
                    'action_suggestion': action_suggestion,
                    'activity_id': activity.get('id', '')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate social draft: {e}")
            return None
    
    async def _get_person_details(self, person_id: str) -> Optional[Dict]:
        """Get person details by ID"""
        try:
            # Query person from Notion
            person_data = await self.notion_client.query_database(
                self.notion_client.db_ids["people"],
                {"property": "id", "title": {"equals": person_id}}
            )
            
            if person_data:
                return person_data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get person details for {person_id}: {e}")
            return None
    
    async def _call_ai_service(self, service_type: str, prompt: str) -> Optional[str]:
        """Call AI service for content generation (placeholder)"""
        # This would integrate with an AI service like OpenAI, Anthropic, etc.
        # For now, return None to use fallback methods
        return None
    
    async def _create_brief_in_notion(self, date: datetime, summary: str, 
                                    action_items: List[Dict], drafts: List[Dict]) -> Optional[str]:
        """Create the daily brief in Notion"""
        try:
            # Prepare brief data
            brief_data = {
                'date': date.date().isoformat(),
                'summary': summary,
                'waiting_on': [item['task_id'] for item in action_items if item.get('task_id')],
                'due_today': [item['task_id'] for item in action_items if item.get('type') == 'due_today'],
                'drafts': self._format_drafts_for_notion(drafts)
            }
            
            # Create brief page
            brief_id = await self.notion_client.create_daily_brief(brief_data)
            
            # Create child pages for detailed action items and drafts
            await self._create_action_items_pages(brief_id, action_items)
            await self._create_drafts_pages(brief_id, drafts)
            
            return brief_id
            
        except Exception as e:
            logger.error(f"Failed to create brief in Notion: {e}")
            return None
    
    def _format_drafts_for_notion(self, drafts: List[Dict]) -> str:
        """Format drafts for Notion rich text"""
        if not drafts:
            return "No drafts generated today."
        
        formatted_drafts = "## Communication Drafts\n\n"
        
        for draft in drafts:
            formatted_drafts += f"### {draft.get('type', 'Unknown').title()} Draft\n"
            formatted_drafts += f"**To:** {draft.get('recipient', 'Unknown')}\n"
            if draft.get('subject'):
                formatted_drafts += f"**Subject:** {draft.get('subject')}\n"
            formatted_drafts += f"**Content:**\n{draft.get('content', '')}\n\n"
        
        return formatted_drafts
    
    async def _create_action_items_pages(self, brief_id: str, action_items: List[Dict]):
        """Create child pages for action items"""
        try:
            for item in action_items:
                page_data = {
                    'title': item.get('title', 'Action Item'),
                    'content': f"**Type:** {item.get('type', 'unknown')}\n"
                              f"**Priority:** {item.get('priority', 'medium')}\n"
                              f"**Description:** {item.get('description', '')}\n"
                }
                
                # Create as child page of brief
                await self.notion_client.create_page(
                    brief_id,  # This would need to be adapted for child pages
                    page_data
                )
                
        except Exception as e:
            logger.error(f"Failed to create action items pages: {e}")
    
    async def _create_drafts_pages(self, brief_id: str, drafts: List[Dict]):
        """Create child pages for drafts"""
        try:
            for draft in drafts:
                page_data = {
                    'title': f"{draft.get('type', 'Draft').title()} Draft",
                    'content': f"**Recipient:** {draft.get('recipient', 'Unknown')}\n"
                              f"**Content:**\n{draft.get('content', '')}\n"
                }
                
                # Create as child page of brief
                await self.notion_client.create_page(
                    brief_id,  # This would need to be adapted for child pages
                    page_data
                )
                
        except Exception as e:
            logger.error(f"Failed to create drafts pages: {e}")

# Example usage
if __name__ == "__main__":
    print("Daily Brief Generator - Ready to use!")
    print("This module generates automated daily briefs with AI-powered insights.")

