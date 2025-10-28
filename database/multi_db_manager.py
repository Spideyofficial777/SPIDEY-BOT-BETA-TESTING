"""
Multi-Database Manager for Spidey Bot
Handles multiple MongoDB database connections for different data types
"""

from motor.motor_asyncio import AsyncIOMotorClient
from info import (
    DATABASE_URI_1, DATABASE_URI_2, DATABASE_URI_3, DATABASE_URI_4, DATABASE_URI_5,
    DATABASE_NAME_1, DATABASE_NAME_2, DATABASE_NAME_3, DATABASE_NAME_4, DATABASE_NAME_5
)
import logging

logger = logging.getLogger(__name__)

class MultiDatabaseManager:
    """
    Manages multiple MongoDB database connections for different data types
    """
    
    def __init__(self):
        self.clients = {}
        self.databases = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize all database connections"""
        db_configs = [
            (1, DATABASE_URI_1, DATABASE_NAME_1, "URL_DATA"),
            (2, DATABASE_URI_2, DATABASE_NAME_2, "USER_DATA"),
            (3, DATABASE_URI_3, DATABASE_NAME_3, "FILE_STORAGE_1"),
            (4, DATABASE_URI_4, DATABASE_NAME_4, "FILE_STORAGE_2"),
            (5, DATABASE_URI_5, DATABASE_NAME_5, "FILE_STORAGE_3")
        ]
        
        for db_id, uri, db_name, purpose in db_configs:
            try:
                client = AsyncIOMotorClient(uri)
                database = client[db_name]
                self.clients[f"db_{db_id}"] = client
                self.databases[f"db_{db_id}"] = database
                logger.info(f"Connected to Database {db_id} ({purpose})")
            except Exception as e:
                logger.error(f"Failed to connect to Database {db_id}: {e}")
                # Create a fallback connection to the main database
                try:
                    from info import DATABASE_URI, DATABASE_NAME
                    client = AsyncIOMotorClient(DATABASE_URI)
                    database = client[DATABASE_NAME]
                    self.clients[f"db_{db_id}"] = client
                    self.databases[f"db_{db_id}"] = database
                    logger.warning(f"Using fallback database for DB {db_id}")
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed for Database {db_id}: {fallback_error}")
    
    def get_database(self, db_type="url_data"):
        """
        Get database connection based on data type
        
        Args:
            db_type (str): Type of data to store
                - "url_data": For URL-related data (DB 1)
                - "user_data": For user-related data (DB 2)
                - "group_data": For group-related data (DB 3)
                - "config_data": For configuration data (DB 4)
                - "backup_data": For backup data (DB 5)
        
        Returns:
            Database connection object
        """
        db_mapping = {
            "url_data": "db_1",
            "user_data": "db_2", 
            "file_storage_1": "db_3",
            "file_storage_2": "db_4",
            "file_storage_3": "db_5"
        }
        
        db_key = db_mapping.get(db_type, "db_1")  # Default to URL data database
        
        if db_key in self.databases:
            return self.databases[db_key]
        else:
            logger.error(f"Database {db_type} not available, using fallback")
            return self.databases.get("db_1", None)
    
    def get_client(self, db_type="url_data"):
        """
        Get client connection based on data type
        
        Args:
            db_type (str): Type of data to store
        
        Returns:
            Client connection object
        """
        db_mapping = {
            "url_data": "db_1",
            "user_data": "db_2",
            "file_storage_1": "db_3", 
            "file_storage_2": "db_4",
            "file_storage_3": "db_5"
        }
        
        db_key = db_mapping.get(db_type, "db_1")
        
        if db_key in self.clients:
            return self.clients[db_key]
        else:
            logger.error(f"Client {db_type} not available, using fallback")
            return self.clients.get("db_1", None)
    
    async def test_connections(self):
        """Test all database connections"""
        results = {}
        for db_key, client in self.clients.items():
            try:
                # Test connection by pinging the database
                await client.admin.command('ping')
                results[db_key] = "Connected"
            except Exception as e:
                results[db_key] = f"Error: {str(e)}"
        return results
    
    async def get_database_stats(self):
        """Get statistics for all databases"""
        stats = {}
        for db_key, database in self.databases.items():
            try:
                db_stats = await database.command("dbstats")
                stats[db_key] = {
                    "collections": db_stats.get("collections", 0),
                    "dataSize": db_stats.get("dataSize", 0),
                    "storageSize": db_stats.get("storageSize", 0),
                    "indexes": db_stats.get("indexes", 0)
                }
            except Exception as e:
                stats[db_key] = {"error": str(e)}
        return stats
    
    async def close_all_connections(self):
        """Close all database connections"""
        for client in self.clients.values():
            try:
                client.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

# Global instance
multi_db_manager = MultiDatabaseManager()

# Convenience functions for easy access
def get_url_database():
    """Get database for URL data"""
    return multi_db_manager.get_database("url_data")

def get_user_database():
    """Get database for user data"""
    return multi_db_manager.get_database("user_data")

def get_file_storage_1_database():
    """Get database for file storage 1"""
    return multi_db_manager.get_database("file_storage_1")

def get_file_storage_2_database():
    """Get database for file storage 2"""
    return multi_db_manager.get_database("file_storage_2")

def get_file_storage_3_database():
    """Get database for file storage 3"""
    return multi_db_manager.get_database("file_storage_3")
