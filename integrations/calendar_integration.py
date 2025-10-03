#!/usr/bin/env python3
"""
Calendar Integration
Handles Google Calendar API interactions for meeting synchronization
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CalendarIntegration:
    """Google Calendar API integration"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.refresh_token = credentials['refresh_token']
        self.access_token = None
        self.session = None
        
        # Calendar API endpoints
        self.base_url = "https://www.googleapis.com/calendar/v3"
        self.oauth_url = "https://oauth2.googleapis.com/token"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self._refresh_access_token()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _refresh_access_token(self) -> bool:
        """Refresh OAuth access token"""
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with self.session.post(self.oauth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    return True
                else:
                    logger.error(f"Token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Calendar API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.request(method, url, headers=headers, params=params) as response:
                if response.status == 401:
                    # Token expired, refresh and retry
                    await self._refresh_access_token()
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    async with self.session.request(method, url, headers=headers, params=params) as retry_response:
                        return await retry_response.json()
                else:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Calendar API request failed: {e}")
            raise
    
    async def get_recent_meetings(self, hours: int = 24, calendar_id: str = "primary") -> List[Dict]:
        """Get recent meetings from calendar"""
        try:
            # Calculate time range
            now = datetime.now()
            time_min = now - timedelta(hours=hours)
            time_max = now + timedelta(hours=24)  # Include future meetings
            
            params = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 100
            }
            
            response = await self._make_request("GET", f"calendars/{calendar_id}/events", params)
            
            meetings = []
            for event in response.get('items', []):
                meeting_data = await self._parse_meeting_event(event)
                if meeting_data:
                    meetings.append(meeting_data)
            
            return meetings
            
        except Exception as e:
            logger.error(f"Failed to get recent meetings: {e}")
            return []
    
    async def _parse_meeting_event(self, event: Dict) -> Optional[Dict]:
        """Parse calendar event into meeting data"""
        try:
            # Extract basic information
            event_id = event.get('id', '')
            title = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            
            # Parse start and end times
            start_time = self._parse_datetime(event.get('start', {}))
            end_time = self._parse_datetime(event.get('end', {}))
            
            # Extract attendees
            attendees = []
            for attendee in event.get('attendees', []):
                attendee_data = {
                    'email': attendee.get('email', ''),
                    'name': attendee.get('displayName', ''),
                    'response_status': attendee.get('responseStatus', 'needsAction'),
                    'organizer': attendee.get('organizer', False)
                }
                attendees.append(attendee_data)
            
            # Determine meeting type
            meeting_type = self._determine_meeting_type(event)
            
            # Extract meeting link if available
            meeting_link = self._extract_meeting_link(event)
            
            return {
                'event_id': event_id,
                'title': title,
                'description': description,
                'location': location,
                'start_time': start_time.isoformat() if start_time else '',
                'end_time': end_time.isoformat() if end_time else '',
                'attendees': attendees,
                'meeting_type': meeting_type,
                'meeting_link': meeting_link,
                'status': event.get('status', 'confirmed'),
                'created': event.get('created', ''),
                'updated': event.get('updated', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to parse meeting event: {e}")
            return None
    
    def _parse_datetime(self, datetime_obj: Dict) -> Optional[datetime]:
        """Parse datetime from calendar event"""
        try:
            if 'dateTime' in datetime_obj:
                return datetime.fromisoformat(datetime_obj['dateTime'].replace('Z', '+00:00'))
            elif 'date' in datetime_obj:
                return datetime.fromisoformat(datetime_obj['date'] + 'T00:00:00+00:00')
            return None
        except Exception as e:
            logger.error(f"Failed to parse datetime: {e}")
            return None
    
    def _determine_meeting_type(self, event: Dict) -> str:
        """Determine meeting type based on event data"""
        # Check for video conference links
        description = event.get('description', '').lower()
        location = event.get('location', '').lower()
        
        if any(platform in description or platform in location for platform in ['zoom', 'teams', 'meet', 'webex']):
            return 'video_conference'
        elif 'phone' in description or 'phone' in location:
            return 'phone_call'
        elif location:
            return 'in_person'
        else:
            return 'unknown'
    
    def _extract_meeting_link(self, event: Dict) -> str:
        """Extract meeting link from event"""
        description = event.get('description', '')
        location = event.get('location', '')
        
        # Look for common meeting link patterns
        import re
        
        # Zoom links
        zoom_match = re.search(r'https://[a-z0-9.-]*zoom\.us/[a-zA-Z0-9?=&/.-]*', description + ' ' + location)
        if zoom_match:
            return zoom_match.group(0)
        
        # Teams links
        teams_match = re.search(r'https://teams\.microsoft\.com/[a-zA-Z0-9?=&/.-]*', description + ' ' + location)
        if teams_match:
            return teams_match.group(0)
        
        # Google Meet links
        meet_match = re.search(r'https://meet\.google\.com/[a-zA-Z0-9?=&/.-]*', description + ' ' + location)
        if meet_match:
            return meet_match.group(0)
        
        # Webex links
        webex_match = re.search(r'https://[a-z0-9.-]*webex\.com/[a-zA-Z0-9?=&/.-]*', description + ' ' + location)
        if webex_match:
            return webex_match.group(0)
        
        return ''
    
    async def get_upcoming_meetings(self, days: int = 7, calendar_id: str = "primary") -> List[Dict]:
        """Get upcoming meetings"""
        try:
            now = datetime.now()
            time_min = now
            time_max = now + timedelta(days=days)
            
            params = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 100
            }
            
            response = await self._make_request("GET", f"calendars/{calendar_id}/events", params)
            
            meetings = []
            for event in response.get('items', []):
                meeting_data = await self._parse_meeting_event(event)
                if meeting_data:
                    meetings.append(meeting_data)
            
            return meetings
            
        except Exception as e:
            logger.error(f"Failed to get upcoming meetings: {e}")
            return []
    
    async def get_meetings_with_attendee(self, attendee_email: str, days: int = 30) -> List[Dict]:
        """Get meetings with specific attendee"""
        try:
            now = datetime.now()
            time_min = now - timedelta(days=days)
            time_max = now + timedelta(days=days)
            
            params = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 100
            }
            
            response = await self._make_request("GET", "calendars/primary/events", params)
            
            meetings = []
            for event in response.get('items', []):
                # Check if attendee is in the meeting
                attendees = event.get('attendees', [])
                if any(att.get('email', '').lower() == attendee_email.lower() for att in attendees):
                    meeting_data = await self._parse_meeting_event(event)
                    if meeting_data:
                        meetings.append(meeting_data)
            
            return meetings
            
        except Exception as e:
            logger.error(f"Failed to get meetings with attendee {attendee_email}: {e}")
            return []
    
    async def get_contacts_from_meetings(self, meetings: List[Dict]) -> List[Dict]:
        """Extract contact information from meetings"""
        contacts = []
        seen_emails = set()
        
        for meeting in meetings:
            for attendee in meeting.get('attendees', []):
                email = attendee.get('email', '')
                if email and email not in seen_emails:
                    contacts.append({
                        'email': email,
                        'name': attendee.get('name', ''),
                        'source': 'calendar_attendee',
                        'last_interaction': meeting.get('start_time', ''),
                        'meeting_count': 1  # Will be incremented if duplicate
                    })
                    seen_emails.add(email)
        
        return contacts
    
    async def get_calendar_list(self) -> List[Dict]:
        """Get list of accessible calendars"""
        try:
            response = await self._make_request("GET", "users/me/calendarList")
            return response.get('items', [])
        except Exception as e:
            logger.error(f"Failed to get calendar list: {e}")
            return []
    
    async def create_meeting(self, meeting_data: Dict) -> Optional[str]:
        """Create a new meeting"""
        try:
            event = {
                'summary': meeting_data.get('title', ''),
                'description': meeting_data.get('description', ''),
                'location': meeting_data.get('location', ''),
                'start': {
                    'dateTime': meeting_data.get('start_time'),
                    'timeZone': meeting_data.get('timezone', 'UTC')
                },
                'end': {
                    'dateTime': meeting_data.get('end_time'),
                    'timeZone': meeting_data.get('timezone', 'UTC')
                },
                'attendees': [
                    {'email': email} for email in meeting_data.get('attendees', [])
                ]
            }
            
            response = await self._make_request("POST", "calendars/primary/events", event)
            return response.get('id')
            
        except Exception as e:
            logger.error(f"Failed to create meeting: {e}")
            return None

# Example usage
if __name__ == "__main__":
    print("Calendar Integration - Ready to use!")
    print("This module handles Google Calendar API interactions for meeting synchronization.")

