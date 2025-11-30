"""Base service class for database operations."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from supabase import Client
from app.core.database import get_supabase_client
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseService:
    """Base service class with common database operations."""
    
    def __init__(self, table_name: str):
        """Initialize service with table name."""
        self.table_name = table_name
        self.client: Optional[Client] = get_supabase_client()
        if not self.client:
            logger.warning(f"Supabase client not available for table {table_name}")
    
    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new record in the table."""
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating record in {self.table_name}: {e}")
            return None
    
    def get_by_id(self, record_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = self.client.table(self.table_name).select("*").eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting record {record_id} from {self.table_name}: {e}")
            return None
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all records with pagination."""
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        try:
            response = (self.client.table(self.table_name)
                       .select("*")
                       .range(offset, offset + limit - 1)
                       .execute())
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting records from {self.table_name}: {e}")
            return []
    
    def update(self, record_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        if not self.client:
            logger.error("Supabase client not available")
            return None
        
        try:
            response = (self.client.table(self.table_name)
                       .update(data)
                       .eq("id", record_id)
                       .execute())
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {self.table_name}: {e}")
            return None
    
    def delete(self, record_id: UUID) -> bool:
        """Delete a record by ID."""
        if not self.client:
            logger.error("Supabase client not available")
            return False
        
        try:
            response = self.client.table(self.table_name).delete().eq("id", record_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {self.table_name}: {e}")
            return False
    
    def count(self) -> int:
        """Count total records in table."""
        if not self.client:
            logger.error("Supabase client not available")
            return 0
        
        try:
            response = self.client.table(self.table_name).select("*", count="exact").execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error counting records in {self.table_name}: {e}")
            return 0
    
    def search(self, query: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """Search records by text query."""
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        try:
            if not fields:
                fields = ["*"]
            
            query_builder = self.client.table(self.table_name).select(",".join(fields))
            
            # Use text search for query
            search_conditions = []
            for field in fields:
                if field != "*":
                    search_conditions.append(f"{field}.ilike.%{query}%")
            
            if search_conditions:
                response = query_builder.or_(",".join(search_conditions)).execute()
            else:
                response = query_builder.execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error searching records in {self.table_name}: {e}")
            return []
    
    def filter(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Filter records by field conditions."""
        if not self.client:
            logger.error("Supabase client not available")
            return []
        
        try:
            query_builder = self.client.table(self.table_name).select("*")
            
            for field, value in filters.items():
                if isinstance(value, list):
                    query_builder = query_builder.in_(field, value)
                else:
                    query_builder = query_builder.eq(field, value)
            
            response = query_builder.range(offset, offset + limit - 1).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error filtering records in {self.table_name}: {e}")
            return []