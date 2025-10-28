"""
Database Router for Spidey Bot
Routes different types of data to appropriate databases
"""

from database.multi_db_manager import multi_db_manager
import logging

logger = logging.getLogger(__name__)

class DatabaseRouter:
    """
    Routes different data types to appropriate databases
    """
    
    def __init__(self):
        self.db_mapping = {
            # URL and link data
            "url_data": "url_data",
            "shortener_data": "url_data", 
            "link_data": "url_data",
            "redirect_data": "url_data",
            
            # User-related data
            "user_data": "user_data",
            "user_profile": "user_data",
            "user_settings": "user_data",
            "user_preferences": "user_data",
            "user_points": "user_data",
            "user_premium": "user_data",
            "user_verification": "user_data",
            "user_requests": "user_data",
            "user_misc": "user_data",
            
            # File storage databases
            "file_storage_1": "file_storage_1",
            "file_storage_2": "file_storage_2", 
            "file_storage_3": "file_storage_3",
            "database_files": "file_storage_1",
            "backup_files": "file_storage_2",
            "archive_files": "file_storage_3",
            "media_files": "file_storage_1",
            "document_files": "file_storage_2",
            "log_files": "file_storage_3"
        }
    
    def get_database_for_data_type(self, data_type):
        """
        Get the appropriate database for a given data type
        
        Args:
            data_type (str): Type of data to store
            
        Returns:
            Database connection object
        """
        db_type = self.db_mapping.get(data_type, "user_data")  # Default to user_data
        database = multi_db_manager.get_database(db_type)
        return database
    
    def get_collection_for_data_type(self, data_type, collection_name):
        """
        Get the appropriate collection for a given data type and collection name
        
        Args:
            data_type (str): Type of data to store
            collection_name (str): Name of the collection
            
        Returns:
            Collection object
        """
        database = self.get_database_for_data_type(data_type)
        if database is not None:
            return database[collection_name]
        else:
            logger.error(f"Database not available for data type: {data_type}")
            return None
    
    def route_user_data(self, collection_name="users"):
        """Route user-related data to user database"""
        return self.get_collection_for_data_type("user_data", collection_name)
    
    def route_file_storage_1(self, collection_name="files"):
        """Route files to file storage database 1"""
        return self.get_collection_for_data_type("file_storage_1", collection_name)
    
    def route_file_storage_2(self, collection_name="files"):
        """Route files to file storage database 2"""
        return self.get_collection_for_data_type("file_storage_2", collection_name)
    
    def route_file_storage_3(self, collection_name="files"):
        """Route files to file storage database 3"""
        return self.get_collection_for_data_type("file_storage_3", collection_name)
    
    def route_url_data(self, collection_name="urls"):
        """Route URL-related data to URL database"""
        return self.get_collection_for_data_type("url_data", collection_name)
    
    def get_all_databases_status(self):
        """Get status of all databases"""
        return multi_db_manager.test_connections()
    
    def get_database_stats(self):
        """Get statistics for all databases"""
        return multi_db_manager.get_database_stats()

# Global router instance
db_router = DatabaseRouter()

# Convenience functions for common data routing
def get_user_collection(collection_name="users"):
    """Get user data collection"""
    return db_router.route_user_data(collection_name)

def get_file_storage_1_collection(collection_name="files"):
    """Get file storage 1 collection"""
    return db_router.route_file_storage_1(collection_name)

def get_file_storage_2_collection(collection_name="files"):
    """Get file storage 2 collection"""
    return db_router.route_file_storage_2(collection_name)

def get_file_storage_3_collection(collection_name="files"):
    """Get file storage 3 collection"""
    return db_router.route_file_storage_3(collection_name)

def get_url_collection(collection_name="urls"):
    """Get URL data collection"""
    return db_router.route_url_data(collection_name)
