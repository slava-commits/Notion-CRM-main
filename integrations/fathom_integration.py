#!/usr/bin/env python3
"""
Fathom Integration
Handles Fathom API interactions for meeting recording synchronization
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class FathomIntegration:
    """Fathom API integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fathom.video/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Fathom API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Fathom API error: {response.status} - {error_text}")
                    raise Exception(f"Fathom API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"Fathom API request failed: {e}")
            raise
    
    async def get_recent_recordings(self, hours: int = 24) -> List[Dict]:
        """Get recent meeting recordings"""
        try:
            # Calculate timestamp for query
            since_time = datetime.now() - timedelta(hours=hours)
            
            params = {
                'created_after': since_time.isoformat(),
                'limit': 100
            }
            
            response = await self._make_request("GET", "recordings", params)
            
            recordings = []
            for recording in response.get('data', []):
                recording_data = await self._parse_recording(recording)
                if recording_data:
                    recordings.append(recording_data)
            
            return recordings
            
        except Exception as e:
            logger.error(f"Failed to get recent recordings: {e}")
            return []
    
    async def _parse_recording(self, recording: Dict) -> Optional[Dict]:
        """Parse Fathom recording into standardized format"""
        try:
            recording_id = recording.get('id', '')
            title = recording.get('title', 'Untitled Meeting')
            summary = recording.get('summary', '')
            transcript = recording.get('transcript', '')
            
            # Parse timestamps
            created_at = self._parse_timestamp(recording.get('created_at'))
            started_at = self._parse_timestamp(recording.get('started_at'))
            ended_at = self._parse_timestamp(recording.get('ended_at'))
            
            # Extract participants
            participants = []
            for participant in recording.get('participants', []):
                participant_data = {
                    'name': participant.get('name', ''),
                    'email': participant.get('email', ''),
                    'role': participant.get('role', 'participant'),
                    'speaking_time': participant.get('speaking_time', 0),
                    'talk_ratio': participant.get('talk_ratio', 0)
                }
                participants.append(participant_data)
            
            # Extract action items
            action_items = []
            for item in recording.get('action_items', []):
                action_item = {
                    'text': item.get('text', ''),
                    'assignee': item.get('assignee', ''),
                    'due_date': item.get('due_date', ''),
                    'status': item.get('status', 'pending')
                }
                action_items.append(action_item)
            
            # Extract topics/keywords
            topics = recording.get('topics', [])
            keywords = recording.get('keywords', [])
            
            # Get meeting URL
            meeting_url = recording.get('url', '')
            
            return {
                'recording_id': recording_id,
                'title': title,
                'summary': summary,
                'transcript': transcript,
                'created_at': created_at.isoformat() if created_at else '',
                'started_at': started_at.isoformat() if started_at else '',
                'ended_at': ended_at.isoformat() if ended_at else '',
                'participants': participants,
                'action_items': action_items,
                'topics': topics,
                'keywords': keywords,
                'meeting_url': meeting_url,
                'duration': recording.get('duration', 0),
                'meeting_type': recording.get('meeting_type', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to parse recording: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime"""
        if not timestamp_str:
            return None
        
        try:
            # Handle ISO format timestamps
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Failed to parse timestamp '{timestamp_str}': {e}")
            return None
    
    async def get_recording_by_id(self, recording_id: str) -> Optional[Dict]:
        """Get specific recording by ID"""
        try:
            response = await self._make_request("GET", f"recordings/{recording_id}")
            return await self._parse_recording(response.get('data', {}))
        except Exception as e:
            logger.error(f"Failed to get recording {recording_id}: {e}")
            return None
    
    async def get_recordings_by_participant(self, participant_email: str, days: int = 30) -> List[Dict]:
        """Get recordings with specific participant"""
        try:
            since_time = datetime.now() - timedelta(days=days)
            
            params = {
                'created_after': since_time.isoformat(),
                'participant_email': participant_email,
                'limit': 100
            }
            
            response = await self._make_request("GET", "recordings", params)
            
            recordings = []
            for recording in response.get('data', []):
                recording_data = await self._parse_recording(recording)
                if recording_data:
                    recordings.append(recording_data)
            
            return recordings
            
        except Exception as e:
            logger.error(f"Failed to get recordings for participant {participant_email}: {e}")
            return []
    
    async def get_action_items(self, recording_id: Optional[str] = None) -> List[Dict]:
        """Get action items from recordings"""
        try:
            if recording_id:
                # Get action items for specific recording
                recording = await self.get_recording_by_id(recording_id)
                return recording.get('action_items', []) if recording else []
            else:
                # Get all recent action items
                recordings = await self.get_recent_recordings(hours=24*7)  # Last week
                all_action_items = []
                
                for recording in recordings:
                    all_action_items.extend(recording.get('action_items', []))
                
                return all_action_items
                
        except Exception as e:
            logger.error(f"Failed to get action items: {e}")
            return []
    
    async def get_contacts_from_recordings(self, recordings: List[Dict]) -> List[Dict]:
        """Extract contact information from recordings"""
        contacts = []
        seen_emails = set()
        
        for recording in recordings:
            for participant in recording.get('participants', []):
                email = participant.get('email', '')
                if email and email not in seen_emails:
                    contacts.append({
                        'email': email,
                        'name': participant.get('name', ''),
                        'source': 'fathom_participant',
                        'last_interaction': recording.get('created_at', ''),
                        'meeting_count': 1,
                        'speaking_time': participant.get('speaking_time', 0),
                        'talk_ratio': participant.get('talk_ratio', 0)
                    })
                    seen_emails.add(email)
        
        return contacts
    
    async def search_recordings(self, query: str, days: int = 30) -> List[Dict]:
        """Search recordings by content"""
        try:
            since_time = datetime.now() - timedelta(days=days)
            
            params = {
                'created_after': since_time.isoformat(),
                'search': query,
                'limit': 100
            }
            
            response = await self._make_request("GET", "recordings", params)
            
            recordings = []
            for recording in response.get('data', []):
                recording_data = await self._parse_recording(recording)
                if recording_data:
                    recordings.append(recording_data)
            
            return recordings
            
        except Exception as e:
            logger.error(f"Recording search failed: {e}")
            return []
    
    async def get_meeting_insights(self, recording_id: str) -> Optional[Dict]:
        """Get detailed insights for a meeting"""
        try:
            response = await self._make_request("GET", f"recordings/{recording_id}/insights")
            
            insights = response.get('data', {})
            
            return {
                'sentiment_analysis': insights.get('sentiment_analysis', {}),
                'speaking_patterns': insights.get('speaking_patterns', {}),
                'engagement_metrics': insights.get('engagement_metrics', {}),
                'key_decisions': insights.get('key_decisions', []),
                'follow_up_items': insights.get('follow_up_items', []),
                'meeting_effectiveness': insights.get('meeting_effectiveness', {})
            }
            
        except Exception as e:
            logger.error(f"Failed to get insights for recording {recording_id}: {e}")
            return None
    
    async def create_action_item(self, recording_id: str, action_item: Dict) -> Optional[str]:
        """Create action item for a recording"""
        try:
            data = {
                'recording_id': recording_id,
                'text': action_item.get('text', ''),
                'assignee': action_item.get('assignee', ''),
                'due_date': action_item.get('due_date', ''),
                'priority': action_item.get('priority', 'medium')
            }
            
            response = await self._make_request("POST", "action_items", data)
            return response.get('data', {}).get('id')
            
        except Exception as e:
            logger.error(f"Failed to create action item: {e}")
            return None
    
    async def get_recording_transcript(self, recording_id: str) -> Optional[str]:
        """Get full transcript for a recording"""
        try:
            response = await self._make_request("GET", f"recordings/{recording_id}/transcript")
            return response.get('data', {}).get('transcript', '')
        except Exception as e:
            logger.error(f"Failed to get transcript for recording {recording_id}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    print("Fathom Integration - Ready to use!")
    print("This module handles Fathom API interactions for meeting recording synchronization.")

