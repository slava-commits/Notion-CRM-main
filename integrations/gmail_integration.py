#!/usr/bin/env python3
"""
Gmail Integration
Handles Gmail API interactions for email synchronization
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import base64
import email
import re

logger = logging.getLogger(__name__)

class GmailIntegration:
    """Gmail API integration"""
    
    def __init__(self, credentials: Dict[str, str]):
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.refresh_token = credentials['refresh_token']
        self.access_token = None
        self.session = None
        
        # Gmail API endpoints
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
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
        """Make authenticated request to Gmail API"""
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
            logger.error(f"Gmail API request failed: {e}")
            raise
    
    async def get_recent_emails(self, hours: int = 24, max_results: int = 100) -> List[Dict]:
        """Get recent emails"""
        try:
            # Calculate timestamp for query
            since_time = datetime.now() - timedelta(hours=hours)
            query = f"after:{int(since_time.timestamp())}"
            
            # Get message IDs
            params = {
                'q': query,
                'maxResults': max_results
            }
            
            response = await self._make_request("GET", "users/me/messages", params)
            message_ids = [msg['id'] for msg in response.get('messages', [])]
            
            # Get full message details
            emails = []
            for message_id in message_ids:
                email_data = await self._get_email_details(message_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Failed to get recent emails: {e}")
            return []
    
    async def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed email information"""
        try:
            response = await self._make_request("GET", f"users/me/messages/{message_id}")
            
            headers = response.get('payload', {}).get('headers', [])
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract basic information
            subject = header_dict.get('subject', '')
            from_header = header_dict.get('from', '')
            to_header = header_dict.get('to', '')
            date_str = header_dict.get('date', '')
            
            # Parse sender information
            from_email, from_name = self._parse_email_address(from_header)
            to_email, to_name = self._parse_email_address(to_header)
            
            # Determine direction
            user_email = await self._get_user_email()
            direction = 'inbound' if from_email != user_email else 'outbound'
            
            # Extract body snippet
            snippet = response.get('snippet', '')
            
            # Parse date
            try:
                timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            return {
                'message_id': message_id,
                'subject': subject,
                'from_email': from_email,
                'from_name': from_name,
                'to_email': to_email,
                'to_name': to_name,
                'direction': direction,
                'timestamp': timestamp.isoformat(),
                'snippet': snippet,
                'thread_id': response.get('threadId', ''),
                'labels': response.get('labelIds', [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get email details for {message_id}: {e}")
            return None
    
    def _parse_email_address(self, email_string: str) -> tuple[str, str]:
        """Parse email address and name from header"""
        if not email_string:
            return '', ''
        
        try:
            # Handle format: "Name <email@domain.com>"
            match = re.match(r'^(.+?)\s*<(.+?)>$', email_string)
            if match:
                name = match.group(1).strip().strip('"')
                email_addr = match.group(2).strip()
                return email_addr, name
            
            # Handle format: "email@domain.com"
            if '@' in email_string:
                return email_string.strip(), ''
            
            return '', email_string.strip()
            
        except Exception as e:
            logger.error(f"Failed to parse email address '{email_string}': {e}")
            return email_string, ''
    
    async def _get_user_email(self) -> str:
        """Get the authenticated user's email address"""
        try:
            response = await self._make_request("GET", "users/me/profile")
            return response.get('emailAddress', '')
        except Exception as e:
            logger.error(f"Failed to get user email: {e}")
            return ''
    
    async def get_email_thread(self, thread_id: str) -> List[Dict]:
        """Get all emails in a thread"""
        try:
            response = await self._make_request("GET", f"users/me/threads/{thread_id}")
            
            emails = []
            for message in response.get('messages', []):
                email_data = await self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Failed to get thread {thread_id}: {e}")
            return []
    
    async def search_emails(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search emails with custom query"""
        try:
            params = {
                'q': query,
                'maxResults': max_results
            }
            
            response = await self._make_request("GET", "users/me/messages", params)
            message_ids = [msg['id'] for msg in response.get('messages', [])]
            
            # Get full message details
            emails = []
            for message_id in message_ids:
                email_data = await self._get_email_details(message_id)
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            logger.error(f"Email search failed: {e}")
            return []
    
    async def get_contacts_from_emails(self, emails: List[Dict]) -> List[Dict]:
        """Extract contact information from emails"""
        contacts = []
        seen_emails = set()
        
        for email_data in emails:
            # Process sender
            sender_email = email_data.get('from_email', '')
            if sender_email and sender_email not in seen_emails:
                contacts.append({
                    'email': sender_email,
                    'name': email_data['from_name'],
                    'source': 'gmail_sender',
                    'last_interaction': email_data['timestamp']
                })
                seen_emails.add(sender_email)
            
            # Process recipient (for outbound emails)
            if email_data.get('direction') == 'outbound':
                recipient_email = email_data.get('to_email', '')
                if recipient_email and recipient_email not in seen_emails:
                    contacts.append({
                        'email': recipient_email,
                        'name': email_data['to_name'],
                        'source': 'gmail_recipient',
                        'last_interaction': email_data['timestamp']
                    })
                    seen_emails.add(recipient_email)
        
        return contacts
    
    async def get_unread_emails(self, max_results: int = 50) -> List[Dict]:
        """Get unread emails"""
        return await self.search_emails("is:unread", max_results)
    
    async def get_emails_from_sender(self, sender_email: str, max_results: int = 50) -> List[Dict]:
        """Get emails from specific sender"""
        query = f"from:{sender_email}"
        return await self.search_emails(query, max_results)
    
    async def get_emails_with_label(self, label: str, max_results: int = 50) -> List[Dict]:
        """Get emails with specific label"""
        query = f"label:{label}"
        return await self.search_emails(query, max_results)

# Example usage
if __name__ == "__main__":
    print("Gmail Integration - Ready to use!")
    print("This module handles Gmail API interactions for email synchronization.")
