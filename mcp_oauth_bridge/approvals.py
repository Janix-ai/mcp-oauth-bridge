"""
Unified approval system for MCP OAuth Bridge

Manages tool call approvals for both OpenAI and Anthropic APIs.
Provides a web UI for approving or denying tool calls.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import json


class ApprovalStatus(str, Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved" 
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Approval request data structure"""
    id: str
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]
    description: str
    timestamp: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    expires_at: Optional[str] = None
    approved_by: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if approval request has expired"""
        if not self.expires_at:
            return False
        
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.now(timezone.utc) >= expiry
        except (ValueError, AttributeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class ApprovalManager:
    """Manages approval requests and responses"""
    
    def __init__(self, default_timeout_minutes: int = 30) -> None:
        """Initialize approval manager
        
        Args:
            default_timeout_minutes: Default timeout for approval requests
        """
        self.default_timeout_minutes = default_timeout_minutes
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_futures: Dict[str, asyncio.Future] = {}
        self.approval_callbacks: List[Callable[[ApprovalRequest], None]] = []
    
    def add_approval_callback(self, callback: Callable[[ApprovalRequest], None]) -> None:
        """Add callback to be notified of approval events
        
        Args:
            callback: Function to call when approval status changes
        """
        self.approval_callbacks.append(callback)
    
    def _notify_callbacks(self, request: ApprovalRequest) -> None:
        """Notify all callbacks of approval status change
        
        Args:
            request: Approval request that changed
        """
        for callback in self.approval_callbacks:
            try:
                callback(request)
            except Exception as e:
                print(f"⚠️  Approval callback error: {e}")
    
    async def request_approval(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        description: str,
        timeout_minutes: Optional[int] = None
    ) -> bool:
        """Request approval for a tool call
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool being called
            arguments: Tool arguments
            description: Human-readable description
            timeout_minutes: Custom timeout, uses default if None
            
        Returns:
            True if approved, False if denied or timed out
        """
        request_id = str(uuid.uuid4())
        timeout = timeout_minutes or self.default_timeout_minutes
        
        # Calculate expiry time
        expires_at = datetime.now(timezone.utc)
        expires_at = expires_at.replace(microsecond=0)  # Remove microseconds for cleaner timestamps
        expires_at = expires_at.replace(second=expires_at.second + (timeout * 60))
        
        # Create approval request
        request = ApprovalRequest(
            id=request_id,
            server_name=server_name,
            tool_name=tool_name,
            arguments=arguments,
            description=description,
            timestamp=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at.isoformat()
        )
        
        # Store request and create future for waiting
        self.pending_requests[request_id] = request
        future = asyncio.Future()
        self.approval_futures[request_id] = future
        
        print(f"🔔 Approval required for {server_name}.{tool_name}")
        print(f"📋 Request ID: {request_id}")
        print(f"📋 Description: {description}")
        print(f"⏰ Expires at: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Notify callbacks
        self._notify_callbacks(request)
        
        try:
            # Wait for approval or timeout
            result = await asyncio.wait_for(future, timeout=timeout * 60)
            return result
        except asyncio.TimeoutError:
            # Mark as expired
            request.status = ApprovalStatus.EXPIRED
            self._notify_callbacks(request)
            print(f"⏰ Approval request {request_id} expired")
            return False
        finally:
            # Clean up
            self.pending_requests.pop(request_id, None)
            self.approval_futures.pop(request_id, None)
    
    def approve_request(self, request_id: str, approved_by: str = "user") -> bool:
        """Approve a pending request
        
        Args:
            request_id: ID of the request to approve
            approved_by: Who approved the request
            
        Returns:
            True if request was approved, False if not found or already resolved
        """
        request = self.pending_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        if request.is_expired():
            request.status = ApprovalStatus.EXPIRED
            self._notify_callbacks(request)
            return False
        
        # Approve the request
        request.status = ApprovalStatus.APPROVED
        request.approved_by = approved_by
        
        # Resolve the future
        future = self.approval_futures.get(request_id)
        if future and not future.done():
            future.set_result(True)
        
        print(f"✅ Approved: {request.server_name}.{request.tool_name} by {approved_by}")
        self._notify_callbacks(request)
        return True
    
    def deny_request(self, request_id: str, denied_by: str = "user") -> bool:
        """Deny a pending request
        
        Args:
            request_id: ID of the request to deny
            denied_by: Who denied the request
            
        Returns:
            True if request was denied, False if not found or already resolved
        """
        request = self.pending_requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        # Deny the request
        request.status = ApprovalStatus.DENIED
        request.approved_by = denied_by
        
        # Resolve the future
        future = self.approval_futures.get(request_id)
        if future and not future.done():
            future.set_result(False)
        
        print(f"❌ Denied: {request.server_name}.{request.tool_name} by {denied_by}")
        self._notify_callbacks(request)
        return True
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests
        
        Returns:
            List of pending requests
        """
        # Clean up expired requests first
        self._cleanup_expired_requests()
        
        return [
            request for request in self.pending_requests.values()
            if request.status == ApprovalStatus.PENDING
        ]
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific approval request
        
        Args:
            request_id: Request ID
            
        Returns:
            Approval request or None if not found
        """
        return self.pending_requests.get(request_id)
    
    def _cleanup_expired_requests(self) -> None:
        """Clean up expired requests"""
        expired_ids = []
        
        for request_id, request in self.pending_requests.items():
            if request.status == ApprovalStatus.PENDING and request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                
                # Resolve future with False
                future = self.approval_futures.get(request_id)
                if future and not future.done():
                    future.set_result(False)
                
                expired_ids.append(request_id)
                self._notify_callbacks(request)
        
        for request_id in expired_ids:
            print(f"⏰ Cleaned up expired approval request: {request_id}")
    
    def get_approval_stats(self) -> Dict[str, int]:
        """Get approval statistics
        
        Returns:
            Dictionary with approval stats
        """
        stats = {
            'pending': 0,
            'approved': 0,
            'denied': 0,
            'expired': 0,
            'total': len(self.pending_requests)
        }
        
        for request in self.pending_requests.values():
            if request.status == ApprovalStatus.PENDING:
                if request.is_expired():
                    stats['expired'] += 1
                else:
                    stats['pending'] += 1
            else:
                stats[request.status.value] += 1
        
        return stats


# Global approval manager instance
_approval_manager: Optional[ApprovalManager] = None


def get_approval_manager() -> ApprovalManager:
    """Get the global approval manager instance"""
    global _approval_manager
    if _approval_manager is None:
        _approval_manager = ApprovalManager()
    return _approval_manager


def reset_approval_manager() -> None:
    """Reset the global approval manager (mainly for testing)"""
    global _approval_manager
    _approval_manager = None 