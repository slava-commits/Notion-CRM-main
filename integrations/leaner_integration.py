#!/usr/bin/env python3
"""
Leaner Integration
Handles Leaner API interactions for task synchronization
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class LeanerIntegration:
    """Leaner API integration for task management"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.leaner.com/v1"  # Assuming Leaner API endpoint
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Leaner API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Leaner API error: {response.status} - {error_text}")
                    raise Exception(f"Leaner API error: {response.status}")
                
                return await response.json()
                
        except Exception as e:
            logger.error(f"Leaner API request failed: {e}")
            raise
    
    async def get_tasks(self, status_filter: Optional[str] = None, 
                       assignee_filter: Optional[str] = None) -> List[Dict]:
        """Get tasks from Leaner"""
        try:
            params = {}
            if status_filter:
                params['status'] = status_filter
            if assignee_filter:
                params['assignee'] = assignee_filter
            
            response = await self._make_request("GET", "tasks", params)
            
            tasks = []
            for task in response.get('data', []):
                task_data = await self._parse_task(task)
                if task_data:
                    tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    async def _parse_task(self, task: Dict) -> Optional[Dict]:
        """Parse Leaner task into standardized format"""
        try:
            task_id = task.get('id', '')
            title = task.get('title', '')
            description = task.get('description', '')
            status = task.get('status', 'todo')
            priority = task.get('priority', 'medium')
            
            # Parse timestamps
            created_at = self._parse_timestamp(task.get('created_at'))
            updated_at = self._parse_timestamp(task.get('updated_at'))
            due_date = self._parse_timestamp(task.get('due_date'))
            
            # Extract assignee information
            assignee = task.get('assignee', {})
            assignee_data = {
                'id': assignee.get('id', ''),
                'name': assignee.get('name', ''),
                'email': assignee.get('email', '')
            }
            
            # Extract project information
            project = task.get('project', {})
            project_data = {
                'id': project.get('id', ''),
                'name': project.get('name', ''),
                'description': project.get('description', '')
            }
            
            # Extract tags
            tags = task.get('tags', [])
            
            # Extract custom fields
            custom_fields = task.get('custom_fields', {})
            
            return {
                'id': task_id,
                'title': title,
                'description': description,
                'status': status,
                'priority': priority,
                'created_at': created_at.isoformat() if created_at else '',
                'updated_at': updated_at.isoformat() if updated_at else '',
                'due_date': due_date.isoformat() if due_date else '',
                'assignee': assignee_data,
                'project': project_data,
                'tags': tags,
                'custom_fields': custom_fields,
                'url': task.get('url', ''),
                'completed_at': self._parse_timestamp(task.get('completed_at'))
            }
            
        except Exception as e:
            logger.error(f"Failed to parse task: {e}")
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
    
    async def create_task(self, task_data: Dict) -> Optional[str]:
        """Create a new task in Leaner"""
        try:
            data = {
                'title': task_data.get('title', ''),
                'description': task_data.get('description', ''),
                'status': task_data.get('status', 'todo'),
                'priority': task_data.get('priority', 'medium'),
                'assignee_id': task_data.get('assignee_id'),
                'project_id': task_data.get('project_id'),
                'due_date': task_data.get('due_date'),
                'tags': task_data.get('tags', []),
                'custom_fields': task_data.get('custom_fields', {})
            }
            
            response = await self._make_request("POST", "tasks", data)
            return response.get('data', {}).get('id')
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing task in Leaner"""
        try:
            data = {}
            
            # Map updates to Leaner API format
            if 'status' in updates:
                data['status'] = updates['status']
            if 'title' in updates:
                data['title'] = updates['title']
            if 'description' in updates:
                data['description'] = updates['description']
            if 'priority' in updates:
                data['priority'] = updates['priority']
            if 'due_date' in updates:
                data['due_date'] = updates['due_date']
            if 'assignee_id' in updates:
                data['assignee_id'] = updates['assignee_id']
            if 'project_id' in updates:
                data['project_id'] = updates['project_id']
            if 'tags' in updates:
                data['tags'] = updates['tags']
            if 'custom_fields' in updates:
                data['custom_fields'] = updates['custom_fields']
            
            await self._make_request("PATCH", f"tasks/{task_id}", data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return False
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task from Leaner"""
        try:
            await self._make_request("DELETE", f"tasks/{task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    async def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get specific task by ID"""
        try:
            response = await self._make_request("GET", f"tasks/{task_id}")
            return await self._parse_task(response.get('data', {}))
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    async def get_tasks_by_project(self, project_id: str) -> List[Dict]:
        """Get tasks for a specific project"""
        try:
            response = await self._make_request("GET", f"projects/{project_id}/tasks")
            
            tasks = []
            for task in response.get('data', []):
                task_data = await self._parse_task(task)
                if task_data:
                    tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks for project {project_id}: {e}")
            return []
    
    async def get_tasks_by_assignee(self, assignee_id: str) -> List[Dict]:
        """Get tasks assigned to a specific user"""
        try:
            response = await self._make_request("GET", f"users/{assignee_id}/tasks")
            
            tasks = []
            for task in response.get('data', []):
                task_data = await self._parse_task(task)
                if task_data:
                    tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks for assignee {assignee_id}: {e}")
            return []
    
    async def get_overdue_tasks(self) -> List[Dict]:
        """Get overdue tasks"""
        try:
            now = datetime.now()
            params = {
                'due_before': now.isoformat(),
                'status': 'todo,doing'  # Only active tasks
            }
            
            response = await self._make_request("GET", "tasks", params)
            
            tasks = []
            for task in response.get('data', []):
                task_data = await self._parse_task(task)
                if task_data:
                    tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {e}")
            return []
    
    async def get_tasks_due_today(self) -> List[Dict]:
        """Get tasks due today"""
        try:
            today = datetime.now().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            
            params = {
                'due_after': start_of_day.isoformat(),
                'due_before': end_of_day.isoformat(),
                'status': 'todo,doing'
            }
            
            response = await self._make_request("GET", "tasks", params)
            
            tasks = []
            for task in response.get('data', []):
                task_data = await self._parse_task(task)
                if task_data:
                    tasks.append(task_data)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks due today: {e}")
            return []
    
    async def get_projects(self) -> List[Dict]:
        """Get all projects"""
        try:
            response = await self._make_request("GET", "projects")
            
            projects = []
            for project in response.get('data', []):
                project_data = {
                    'id': project.get('id', ''),
                    'name': project.get('name', ''),
                    'description': project.get('description', ''),
                    'status': project.get('status', 'active'),
                    'created_at': self._parse_timestamp(project.get('created_at')),
                    'updated_at': self._parse_timestamp(project.get('updated_at')),
                    'owner': project.get('owner', {}),
                    'members': project.get('members', [])
                }
                projects.append(project_data)
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    async def get_users(self) -> List[Dict]:
        """Get all users"""
        try:
            response = await self._make_request("GET", "users")
            
            users = []
            for user in response.get('data', []):
                user_data = {
                    'id': user.get('id', ''),
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'role': user.get('role', 'user'),
                    'status': user.get('status', 'active'),
                    'created_at': self._parse_timestamp(user.get('created_at')),
                    'last_login': self._parse_timestamp(user.get('last_login'))
                }
                users.append(user_data)
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    async def sync_task_status(self, notion_task_id: str, leaner_task_id: str, 
                              notion_status: str) -> bool:
        """Sync task status from Notion to Leaner"""
        try:
            # Map Notion status to Leaner status
            status_mapping = {
                'Todo': 'todo',
                'Doing': 'doing',
                'Blocked': 'blocked',
                'Done': 'completed'
            }
            
            leaner_status = status_mapping.get(notion_status, 'todo')
            
            return await self.update_task(leaner_task_id, {'status': leaner_status})
            
        except Exception as e:
            logger.error(f"Failed to sync task status: {e}")
            return False
    
    async def create_task_from_notion(self, notion_task_data: Dict) -> Optional[str]:
        """Create Leaner task from Notion task data"""
        try:
            # Map Notion task data to Leaner format
            leaner_data = {
                'title': notion_task_data.get('title', ''),
                'description': notion_task_data.get('description', ''),
                'status': self._map_notion_status_to_leaner(notion_task_data.get('status', 'Todo')),
                'priority': self._map_notion_priority_to_leaner(notion_task_data.get('priority', 'Medium')),
                'due_date': notion_task_data.get('due_date'),
                'tags': notion_task_data.get('tags', []),
                'custom_fields': {
                    'notion_id': notion_task_data.get('notion_id', ''),
                    'reason': notion_task_data.get('reason', ''),
                    'person_id': notion_task_data.get('person_id', ''),
                    'company_id': notion_task_data.get('company_id', ''),
                    'thread_id': notion_task_data.get('thread_id', '')
                }
            }
            
            return await self.create_task(leaner_data)
            
        except Exception as e:
            logger.error(f"Failed to create Leaner task from Notion data: {e}")
            return None
    
    def _map_notion_status_to_leaner(self, notion_status: str) -> str:
        """Map Notion task status to Leaner status"""
        mapping = {
            'Todo': 'todo',
            'Doing': 'doing',
            'Blocked': 'blocked',
            'Done': 'completed'
        }
        return mapping.get(notion_status, 'todo')
    
    def _map_notion_priority_to_leaner(self, notion_priority: str) -> str:
        """Map Notion task priority to Leaner priority"""
        mapping = {
            'High': 'high',
            'Medium': 'medium',
            'Low': 'low'
        }
        return mapping.get(notion_priority, 'medium')

# Example usage
if __name__ == "__main__":
    print("Leaner Integration - Ready to use!")
    print("This module handles Leaner API interactions for task synchronization.")

