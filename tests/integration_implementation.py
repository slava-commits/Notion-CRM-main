#!/usr/bin/env python3
"""
Comprehensive User Data Integration System
Handles Fathom, DocSend, and Email data with sophisticated email deduplication
"""

import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from difflib import SequenceMatcher
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmailAddress:
    """Represents an email address with metadata"""
    address: str
    display_name: Optional[str] = None
    context: str = "unknown"  # personal, professional, temporary
    verified: bool = False
    confidence_score: float = 1.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

@dataclass
class Contact:
    """Enhanced contact representation with multiple email support"""
    contact_id: str
    name: str
    company: Optional[str] = None
    status: str = "active"
    primary_email: Optional[str] = None
    email_addresses: List[EmailAddress] = field(default_factory=list)
    ai_summary: str = ""
    relationship_strength: float = 0.0
    last_contact: Optional[datetime] = None
    communication_preferences: Dict = field(default_factory=dict)
    engagement_metrics: Dict = field(default_factory=dict)

@dataclass
class Event:
    """Universal event structure for all interaction types"""
    event_id: str
    event_type: str  # email, meeting, document, social
    timestamp: datetime
    source_system: str
    related_contacts: List[str] = field(default_factory=list)
    title: str = ""
    description: str = ""
    metadata: Dict = field(default_factory=dict)
    confidence_score: float = 1.0

class EmailDeduplicationEngine:
    """Advanced email deduplication and contact matching engine"""
    
    def __init__(self):
        self.contacts: Dict[str, Contact] = {}
        self.email_registry: Dict[str, List[str]] = {}  # email -> contact_ids
        self.name_variations: Dict[str, Set[str]] = {}  # normalized_name -> variations
        
    def normalize_name(self, name: str) -> str:
        """Normalize name for matching purposes"""
        if not name:
            return ""
        
        # Remove titles and suffixes
        name = re.sub(r'\b(mr|mrs|ms|dr|prof|jr|sr|ii|iii)\b\.?', '', name.lower())
        # Remove extra whitespace and punctuation
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())
        return name
    
    def extract_domain_info(self, email: str) -> Tuple[str, str]:
        """Extract username and domain from email"""
        if '@' not in email:
            return email, ""
        username, domain = email.lower().split('@', 1)
        return username, domain
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Check if one is contained in the other (nickname scenarios)
        if norm1 in norm2 or norm2 in norm1:
            return 0.8
        
        # Use sequence matcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Check for name part matches (first/last name swaps)
        parts1 = set(norm1.split())
        parts2 = set(norm2.split())
        if parts1 & parts2:  # Common parts exist
            similarity = max(similarity, 0.7)
        
        return similarity
    
    def find_matching_contacts(self, email: str, name: str = "") -> List[Tuple[str, float]]:
        """Find potential matching contacts for an email/name combination"""
        matches = []
        
        # Direct email match
        if email.lower() in self.email_registry:
            for contact_id in self.email_registry[email.lower()]:
                matches.append((contact_id, 1.0))
        
        # Domain-based matching for same organization
        username, domain = self.extract_domain_info(email)
        
        for contact_id, contact in self.contacts.items():
            confidence = 0.0
            
            # Name similarity matching
            if name and contact.name:
                name_sim = self.calculate_name_similarity(name, contact.name)
                if name_sim > 0.6:
                    confidence = max(confidence, name_sim * 0.8)
            
            # Domain matching with existing emails
            for email_addr in contact.email_addresses:
                _, existing_domain = self.extract_domain_info(email_addr.address)
                if domain and existing_domain == domain and domain != "gmail.com":
                    confidence = max(confidence, 0.6)
            
            # Username similarity in same domain
            if domain and confidence > 0:
                for email_addr in contact.email_addresses:
                    existing_username, existing_domain = self.extract_domain_info(email_addr.address)
                    if existing_domain == domain:
                        username_sim = SequenceMatcher(None, username, existing_username).ratio()
                        if username_sim > 0.7:
                            confidence = max(confidence, 0.8)
            
            if confidence > 0.5:
                matches.append((contact_id, confidence))
        
        # Sort by confidence score
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def add_or_update_contact(self, email: str, name: str = "", 
                            company: str = "", context: str = "unknown") -> str:
        """Add new contact or update existing one"""
        
        # Find potential matches
        matches = self.find_matching_contacts(email, name)
        
        if matches and matches[0][1] > 0.8:  # High confidence match
            contact_id = matches[0][0]
            contact = self.contacts[contact_id]
            
            # Add email if not already present
            email_exists = any(ea.address.lower() == email.lower() 
                             for ea in contact.email_addresses)
            
            if not email_exists:
                email_obj = EmailAddress(
                    address=email.lower(),
                    display_name=name,
                    context=context,
                    confidence_score=matches[0][1]
                )
                contact.email_addresses.append(email_obj)
                
                # Update email registry
                if email.lower() not in self.email_registry:
                    self.email_registry[email.lower()] = []
                self.email_registry[email.lower()].append(contact_id)
            
            # Update contact information if provided
            if name and not contact.name:
                contact.name = name
            if company and not contact.company:
                contact.company = company
                
            return contact_id
        
        else:  # Create new contact
            contact_id = hashlib.md5(f"{email}_{datetime.now().isoformat()}".encode()).hexdigest()
            
            email_obj = EmailAddress(
                address=email.lower(),
                display_name=name,
                context=context,
                verified=True
            )
            
            contact = Contact(
                contact_id=contact_id,
                name=name or email.split('@')[0],
                company=company,
                primary_email=email.lower(),
                email_addresses=[email_obj]
            )
            
            self.contacts[contact_id] = contact
            
            # Update email registry
            if email.lower() not in self.email_registry:
                self.email_registry[email.lower()] = []
            self.email_registry[email.lower()].append(contact_id)
            
            return contact_id

# Example usage
if __name__ == "__main__":
    print("User Data Integration System - Ready to use!")
    print("Next: Create zapier_integration_config.py")

