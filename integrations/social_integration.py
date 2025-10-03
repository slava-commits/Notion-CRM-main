#!/usr/bin/env python3
"""
Social Media Integration
Handles LinkedIn and X (Twitter) API interactions for social activity tracking
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re

logger = logging.getLogger(__name__)

class SocialIntegration:
    """Social media API integration for LinkedIn and X"""
    
    def __init__(self, linkedin_api_key: str, x_api_key: str):
        self.linkedin_api_key = linkedin_api_key
        self.x_api_key = x_api_key
        self.session = None
        
        # API endpoints
        self.linkedin_base_url = "https://api.linkedin.com/v2"
        self.x_base_url = "https://api.twitter.com/2"
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_linkedin_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to LinkedIn API"""
        url = f"{self.linkedin_base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.linkedin_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, params=params) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"LinkedIn API error: {response.status} - {error_text}")
                    raise Exception(f"LinkedIn API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"LinkedIn API request failed: {e}")
            raise
    
    async def _make_x_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to X API"""
        url = f"{self.x_base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.x_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, params=params) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"X API error: {response.status} - {error_text}")
                    raise Exception(f"X API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"X API request failed: {e}")
            raise
    
    async def get_recent_activity(self, hours: int = 24) -> List[Dict]:
        """Get recent social media activity from both platforms"""
        activities = []
        
        # Get LinkedIn activity
        linkedin_activity = await self.get_linkedin_activity(hours)
        activities.extend(linkedin_activity)
        
        # Get X activity
        x_activity = await self.get_x_activity(hours)
        activities.extend(x_activity)
        
        return activities
    
    async def get_linkedin_activity(self, hours: int = 24) -> List[Dict]:
        """Get recent LinkedIn activity"""
        try:
            # Get connections' recent posts
            connections = await self._get_linkedin_connections()
            activities = []
            
            for connection in connections:
                # Get recent posts from connection
                posts = await self._get_linkedin_posts(connection['id'], hours)
                
                for post in posts:
                    activity = {
                        'network': 'LinkedIn',
                        'type': 'Post',
                        'timestamp': post.get('created_time', ''),
                        'url': post.get('url', ''),
                        'name': connection.get('name', ''),
                        'email': connection.get('email', ''),
                        'company': connection.get('company', ''),
                        'content': post.get('text', ''),
                        'engagement': post.get('engagement', {}),
                        'action_suggestion': self._generate_action_suggestion(post, 'LinkedIn')
                    }
                    activities.append(activity)
                
                # Get comments from connection
                comments = await self._get_linkedin_comments(connection['id'], hours)
                
                for comment in comments:
                    activity = {
                        'network': 'LinkedIn',
                        'type': 'Comment',
                        'timestamp': comment.get('created_time', ''),
                        'url': comment.get('url', ''),
                        'name': connection.get('name', ''),
                        'email': connection.get('email', ''),
                        'company': connection.get('company', ''),
                        'content': comment.get('text', ''),
                        'engagement': comment.get('engagement', {}),
                        'action_suggestion': self._generate_action_suggestion(comment, 'LinkedIn')
                    }
                    activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn activity: {e}")
            return []
    
    async def _get_linkedin_connections(self) -> List[Dict]:
        """Get LinkedIn connections"""
        try:
            response = await self._make_linkedin_request("GET", "people/~/connections")
            
            connections = []
            for connection in response.get('values', []):
                conn_data = {
                    'id': connection.get('id', ''),
                    'name': connection.get('firstName', '') + ' ' + connection.get('lastName', ''),
                    'email': connection.get('emailAddress', ''),
                    'company': connection.get('companyName', ''),
                    'title': connection.get('headline', '')
                }
                connections.append(conn_data)
            
            return connections
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn connections: {e}")
            return []
    
    async def _get_linkedin_posts(self, person_id: str, hours: int) -> List[Dict]:
        """Get LinkedIn posts from a person"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            params = {
                'person_id': person_id,
                'created_after': since_time.isoformat(),
                'count': 50
            }
            
            response = await self._make_linkedin_request("GET", "people/{person_id}/posts", params)
            
            posts = []
            for post in response.get('values', []):
                post_data = {
                    'id': post.get('id', ''),
                    'text': post.get('text', ''),
                    'created_time': post.get('created_time', ''),
                    'url': post.get('url', ''),
                    'engagement': {
                        'likes': post.get('likes_count', 0),
                        'comments': post.get('comments_count', 0),
                        'shares': post.get('shares_count', 0)
                    }
                }
                posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn posts for {person_id}: {e}")
            return []
    
    async def _get_linkedin_comments(self, person_id: str, hours: int) -> List[Dict]:
        """Get LinkedIn comments from a person"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            params = {
                'person_id': person_id,
                'created_after': since_time.isoformat(),
                'count': 50
            }
            
            response = await self._make_linkedin_request("GET", "people/{person_id}/comments", params)
            
            comments = []
            for comment in response.get('values', []):
                comment_data = {
                    'id': comment.get('id', ''),
                    'text': comment.get('text', ''),
                    'created_time': comment.get('created_time', ''),
                    'url': comment.get('url', ''),
                    'engagement': {
                        'likes': comment.get('likes_count', 0)
                    }
                }
                comments.append(comment_data)
            
            return comments
            
        except Exception as e:
            logger.error(f"Failed to get LinkedIn comments for {person_id}: {e}")
            return []
    
    async def get_x_activity(self, hours: int = 24) -> List[Dict]:
        """Get recent X (Twitter) activity"""
        try:
            # Get following list
            following = await self._get_x_following()
            activities = []
            
            for user in following:
                # Get recent tweets from user
                tweets = await self._get_x_tweets(user['id'], hours)
                
                for tweet in tweets:
                    activity = {
                        'network': 'X',
                        'type': 'Post',
                        'timestamp': tweet.get('created_at', ''),
                        'url': tweet.get('url', ''),
                        'name': user.get('name', ''),
                        'email': user.get('email', ''),
                        'company': user.get('company', ''),
                        'content': tweet.get('text', ''),
                        'engagement': tweet.get('engagement', {}),
                        'action_suggestion': self._generate_action_suggestion(tweet, 'X')
                    }
                    activities.append(activity)
                
                # Get replies from user
                replies = await self._get_x_replies(user['id'], hours)
                
                for reply in replies:
                    activity = {
                        'network': 'X',
                        'type': 'Comment',
                        'timestamp': reply.get('created_at', ''),
                        'url': reply.get('url', ''),
                        'name': user.get('name', ''),
                        'email': user.get('email', ''),
                        'company': user.get('company', ''),
                        'content': reply.get('text', ''),
                        'engagement': reply.get('engagement', {}),
                        'action_suggestion': self._generate_action_suggestion(reply, 'X')
                    }
                    activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Failed to get X activity: {e}")
            return []
    
    async def _get_x_following(self) -> List[Dict]:
        """Get X following list"""
        try:
            response = await self._make_x_request("GET", "users/me/following")
            
            users = []
            for user in response.get('data', []):
                user_data = {
                    'id': user.get('id', ''),
                    'name': user.get('name', ''),
                    'username': user.get('username', ''),
                    'email': user.get('email', ''),
                    'company': user.get('company', ''),
                    'description': user.get('description', '')
                }
                users.append(user_data)
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to get X following: {e}")
            return []
    
    async def _get_x_tweets(self, user_id: str, hours: int) -> List[Dict]:
        """Get X tweets from a user"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            params = {
                'user_id': user_id,
                'start_time': since_time.isoformat(),
                'max_results': 50
            }
            
            response = await self._make_x_request("GET", f"users/{user_id}/tweets", params)
            
            tweets = []
            for tweet in response.get('data', []):
                tweet_data = {
                    'id': tweet.get('id', ''),
                    'text': tweet.get('text', ''),
                    'created_at': tweet.get('created_at', ''),
                    'url': f"https://twitter.com/{user_id}/status/{tweet.get('id', '')}",
                    'engagement': {
                        'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                        'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                        'replies': tweet.get('public_metrics', {}).get('reply_count', 0)
                    }
                }
                tweets.append(tweet_data)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Failed to get X tweets for {user_id}: {e}")
            return []
    
    async def _get_x_replies(self, user_id: str, hours: int) -> List[Dict]:
        """Get X replies from a user"""
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            params = {
                'user_id': user_id,
                'start_time': since_time.isoformat(),
                'max_results': 50
            }
            
            response = await self._make_x_request("GET", f"users/{user_id}/mentions", params)
            
            replies = []
            for reply in response.get('data', []):
                reply_data = {
                    'id': reply.get('id', ''),
                    'text': reply.get('text', ''),
                    'created_at': reply.get('created_at', ''),
                    'url': f"https://twitter.com/{user_id}/status/{reply.get('id', '')}",
                    'engagement': {
                        'likes': reply.get('public_metrics', {}).get('like_count', 0),
                        'retweets': reply.get('public_metrics', {}).get('retweet_count', 0),
                        'replies': reply.get('public_metrics', {}).get('reply_count', 0)
                    }
                }
                replies.append(reply_data)
            
            return replies
            
        except Exception as e:
            logger.error(f"Failed to get X replies for {user_id}: {e}")
            return []
    
    def _generate_action_suggestion(self, content: Dict, network: str) -> str:
        """Generate action suggestion based on content"""
        text = content.get('text', '').lower()
        engagement = content.get('engagement', {})
        
        # High engagement content
        total_engagement = sum(engagement.values()) if isinstance(engagement, dict) else 0
        
        if total_engagement > 100:
            return f"High engagement {network} post - consider reaching out to congratulate or engage"
        
        # Keywords that suggest business opportunities
        business_keywords = ['funding', 'investment', 'startup', 'hiring', 'partnership', 'collaboration']
        if any(keyword in text for keyword in business_keywords):
            return f"Business opportunity mentioned on {network} - consider reaching out"
        
        # Job changes or announcements
        if any(word in text for word in ['new job', 'joined', 'excited to announce', 'starting at']):
            return f"Career update on {network} - send congratulations message"
        
        # Company milestones
        if any(word in text for word in ['milestone', 'achievement', 'launch', 'anniversary']):
            return f"Company milestone on {network} - send congratulations"
        
        # Default suggestion
        return f"Recent {network} activity - consider engaging with a like or comment"
    
    async def get_contacts_from_activity(self, activities: List[Dict]) -> List[Dict]:
        """Extract contact information from social activity"""
        contacts = []
        seen_emails = set()
        
        for activity in activities:
            email = activity.get('email', '')
            if email and email not in seen_emails:
                contacts.append({
                    'email': email,
                    'name': activity.get('name', ''),
                    'company': activity.get('company', ''),
                    'source': f"{activity.get('network', '').lower()}_activity",
                    'last_interaction': activity.get('timestamp', ''),
                    'social_networks': [activity.get('network', '')],
                    'engagement_level': self._calculate_engagement_level(activity)
                })
                seen_emails.add(email)
        
        return contacts
    
    def _calculate_engagement_level(self, activity: Dict) -> str:
        """Calculate engagement level based on activity"""
        engagement = activity.get('engagement', {})
        total_engagement = sum(engagement.values()) if isinstance(engagement, dict) else 0
        
        if total_engagement > 100:
            return 'high'
        elif total_engagement > 20:
            return 'medium'
        else:
            return 'low'
    
    async def search_social_content(self, query: str, network: Optional[str] = None) -> List[Dict]:
        """Search social media content"""
        results = []
        
        if not network or network.lower() == 'linkedin':
            linkedin_results = await self._search_linkedin_content(query)
            results.extend(linkedin_results)
        
        if not network or network.lower() == 'x':
            x_results = await self._search_x_content(query)
            results.extend(x_results)
        
        return results
    
    async def _search_linkedin_content(self, query: str) -> List[Dict]:
        """Search LinkedIn content"""
        try:
            params = {'q': query, 'count': 50}
            response = await self._make_linkedin_request("GET", "search", params)
            
            results = []
            for item in response.get('elements', []):
                result = {
                    'network': 'LinkedIn',
                    'type': item.get('type', ''),
                    'content': item.get('text', ''),
                    'url': item.get('url', ''),
                    'timestamp': item.get('created_time', ''),
                    'author': item.get('author', {})
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"LinkedIn search failed: {e}")
            return []
    
    async def _search_x_content(self, query: str) -> List[Dict]:
        """Search X content"""
        try:
            params = {'query': query, 'max_results': 50}
            response = await self._make_x_request("GET", "tweets/search/recent", params)
            
            results = []
            for tweet in response.get('data', []):
                result = {
                    'network': 'X',
                    'type': 'Tweet',
                    'content': tweet.get('text', ''),
                    'url': f"https://twitter.com/user/status/{tweet.get('id', '')}",
                    'timestamp': tweet.get('created_at', ''),
                    'author': tweet.get('author_id', '')
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"X search failed: {e}")
            return []

# Example usage
if __name__ == "__main__":
    print("Social Integration - Ready to use!")
    print("This module handles LinkedIn and X API interactions for social activity tracking.")

