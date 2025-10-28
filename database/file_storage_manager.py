"""
File Storage Manager for Spidey Bot
Manages database files across 3 storage databases
"""

import asyncio
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from database.db_router import (
    get_file_storage_1_collection, 
    get_file_storage_2_collection, 
    get_file_storage_3_collection
)
import logging

logger = logging.getLogger(__name__)

class FileStorageManager:
    """
    Manages database files across 3 storage databases
    """
    
    def __init__(self):
        self.storage_1 = get_file_storage_1_collection("database_files")
        self.storage_2 = get_file_storage_2_collection("backup_files")
        self.storage_3 = get_file_storage_3_collection("archive_files")
        
        # File type routing
        self.file_type_mapping = {
            "database": self.storage_1,
            "backup": self.storage_2,
            "archive": self.storage_3,
            "media": self.storage_1,
            "document": self.storage_2,
            "log": self.storage_3
        }
    
    def _get_storage_collection(self, file_type: str = "database"):
        """Get the appropriate storage collection based on file type"""
        return self.file_type_mapping.get(file_type, self.storage_1)
    
    def _generate_file_id(self, file_name: str, file_size: int) -> str:
        """Generate a unique file ID"""
        content = f"{file_name}_{file_size}_{datetime.now().timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def store_file(self, file_name: str, file_content: bytes, 
                        file_type: str = "database", metadata: Dict = None) -> str:
        """
        Store a file in the appropriate storage database
        
        Args:
            file_name (str): Name of the file
            file_content (bytes): File content as bytes
            file_type (str): Type of file (database, backup, archive, media, document, log)
            metadata (Dict): Additional metadata for the file
            
        Returns:
            str: File ID of the stored file
        """
        try:
            file_id = self._generate_file_id(file_name, len(file_content))
            storage_collection = self._get_storage_collection(file_type)
            
            file_document = {
                "file_id": file_id,
                "file_name": file_name,
                "file_size": len(file_content),
                "file_type": file_type,
                "content": file_content,
                "metadata": metadata or {},
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "access_count": 0
            }
            
            await storage_collection.insert_one(file_document)
            logger.info(f"File stored successfully: {file_name} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing file {file_name}: {str(e)}")
            raise
    
    async def retrieve_file(self, file_id: str) -> Optional[Dict]:
        """
        Retrieve a file by its ID
        
        Args:
            file_id (str): File ID to retrieve
            
        Returns:
            Dict: File document with content, or None if not found
        """
        try:
            # Search in all storage collections
            for collection in [self.storage_1, self.storage_2, self.storage_3]:
                file_doc = await collection.find_one({"file_id": file_id})
                if file_doc:
                    # Update access count and last accessed time
                    await collection.update_one(
                        {"file_id": file_id},
                        {
                            "$inc": {"access_count": 1},
                            "$set": {"last_accessed": datetime.now()}
                        }
                    )
                    return file_doc
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {str(e)}")
            return None
    
    async def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Get file information without retrieving the content
        
        Args:
            file_id (str): File ID to get info for
            
        Returns:
            Dict: File information without content, or None if not found
        """
        try:
            for collection in [self.storage_1, self.storage_2, self.storage_3]:
                file_doc = await collection.find_one(
                    {"file_id": file_id},
                    {"content": 0}  # Exclude content from result
                )
                if file_doc:
                    return file_doc
            return None
            
        except Exception as e:
            logger.error(f"Error getting file info {file_id}: {str(e)}")
            return None
    
    async def list_files(self, file_type: str = None, limit: int = 100) -> List[Dict]:
        """
        List files in storage
        
        Args:
            file_type (str): Filter by file type
            limit (int): Maximum number of files to return
            
        Returns:
            List[Dict]: List of file information
        """
        try:
            files = []
            collections_to_search = []
            
            if file_type:
                collections_to_search = [self._get_storage_collection(file_type)]
            else:
                collections_to_search = [self.storage_1, self.storage_2, self.storage_3]
            
            for collection in collections_to_search:
                cursor = collection.find({}, {"content": 0}).limit(limit)
                async for file_doc in cursor:
                    files.append(file_doc)
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_id (str): File ID to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            for collection in [self.storage_1, self.storage_2, self.storage_3]:
                result = await collection.delete_one({"file_id": file_id})
                if result.deleted_count > 0:
                    logger.info(f"File deleted successfully: {file_id}")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            return False
    
    async def update_file_metadata(self, file_id: str, metadata: Dict) -> bool:
        """
        Update file metadata
        
        Args:
            file_id (str): File ID to update
            metadata (Dict): New metadata
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            for collection in [self.storage_1, self.storage_2, self.storage_3]:
                result = await collection.update_one(
                    {"file_id": file_id},
                    {"$set": {"metadata": metadata, "last_accessed": datetime.now()}}
                )
                if result.modified_count > 0:
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating file metadata {file_id}: {str(e)}")
            return False
    
    async def get_storage_stats(self) -> Dict:
        """
        Get storage statistics for all databases
        
        Returns:
            Dict: Storage statistics
        """
        try:
            stats = {}
            collections = [
                ("storage_1", self.storage_1),
                ("storage_2", self.storage_2),
                ("storage_3", self.storage_3)
            ]
            
            for name, collection in collections:
                try:
                    total_files = await collection.count_documents({})
                    total_size = await collection.aggregate([
                        {"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}
                    ]).to_list(1)
                    
                    stats[name] = {
                        "total_files": total_files,
                        "total_size": total_size[0]["total_size"] if total_size else 0
                    }
                except Exception as e:
                    stats[name] = {"error": str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {}
    
    async def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up old files based on creation date
        
        Args:
            days_old (int): Delete files older than this many days
            
        Returns:
            int: Number of files deleted
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
            
            total_deleted = 0
            for collection in [self.storage_1, self.storage_2, self.storage_3]:
                result = await collection.delete_many({
                    "created_at": {"$lt": cutoff_date}
                })
                total_deleted += result.deleted_count
            
            logger.info(f"Cleaned up {total_deleted} old files")
            return total_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {str(e)}")
            return 0

# Global file storage manager instance
file_storage_manager = FileStorageManager()

# Convenience functions
async def store_database_file(file_name: str, file_content: bytes, metadata: Dict = None) -> str:
    """Store a database file"""
    return await file_storage_manager.store_file(file_name, file_content, "database", metadata)

async def store_backup_file(file_name: str, file_content: bytes, metadata: Dict = None) -> str:
    """Store a backup file"""
    return await file_storage_manager.store_file(file_name, file_content, "backup", metadata)

async def store_archive_file(file_name: str, file_content: bytes, metadata: Dict = None) -> str:
    """Store an archive file"""
    return await file_storage_manager.store_file(file_name, file_content, "archive", metadata)

async def retrieve_file_by_id(file_id: str) -> Optional[Dict]:
    """Retrieve a file by ID"""
    return await file_storage_manager.retrieve_file(file_id)

async def get_file_list(file_type: str = None) -> List[Dict]:
    """Get list of files"""
    return await file_storage_manager.list_files(file_type)

async def delete_file_by_id(file_id: str) -> bool:
    """Delete a file by ID"""
    return await file_storage_manager.delete_file(file_id)
