# Multi-Database System for Spidey Bot

## Overview

This implementation adds support for 5 MongoDB databases in your Spidey bot, allowing you to organize different types of data across separate databases for better performance and organization.

## Database Configuration

### Database URLs Added

1. **Database 1 (URL Data)**: `mongodb+srv://bawes77719_db_user:4nZaZZmNR2gxbkSP@cluster0.p1qnxox.mongodb.net/?appName=Cluster0`
2. **Database 2 (User Data)**: `mongodb+srv://degaje2058_db_user:A88eEdqwKbzH7HCi@cluster0.83ijpgp.mongodb.net/?appName=Cluster0`
3. **Database 3 (Group Data)**: `mongodb+srv://spideyofficial777_db_user:XkxpJT1PLv1E0tn7@cluster0.i4ptown.mongodb.net/?appName=Cluster0`
4. **Database 4 (Config Data)**: `mongodb+srv://sihemar872_db_user:m0sFeAWexzrAqvMW@cluster0.5bkummz.mongodb.net/?appName=Cluster0`
5. **Database 5 (Backup Data)**: `mongodb+srv://bawes77719_db_user:4nZaZZmNR2gxbkSP@cluster0.p1qnxox.mongodb.net/?appName=Cluster0`

### Database Purposes

- **Database 1 (URL Data)**: Stores URL shortening data, redirects, and link analytics
- **Database 2 (User Data)**: Stores user profiles, settings, points, premium status, and user-related data
- **Database 3 (File Storage 1)**: Stores database files, media files, and primary file storage
- **Database 4 (File Storage 2)**: Stores backup files, document files, and secondary file storage
- **Database 5 (File Storage 3)**: Stores archive files, log files, and tertiary file storage

## Environment Variables

Add these to your `.env` file or environment:

```bash
# Database 1 - URL Data
DATABASE_URI_1=mongodb+srv://bawes77719_db_user:4nZaZZmNR2gxbkSP@cluster0.p1qnxox.mongodb.net/?appName=Cluster0
DATABASE_NAME_1=SPIDEY_URL_DATA

# Database 2 - User Data
DATABASE_URI_2=mongodb+srv://degaje2058_db_user:A88eEdqwKbzH7HCi@cluster0.83ijpgp.mongodb.net/?appName=Cluster0
DATABASE_NAME_2=SPIDEY_USER_DATA

# Database 3 - File Storage 1
DATABASE_URI_3=mongodb+srv://spideyofficial777_db_user:XkxpJT1PLv1E0tn7@cluster0.i4ptown.mongodb.net/?appName=Cluster0
DATABASE_NAME_3=SPIDEY_FILE_STORAGE_1

# Database 4 - File Storage 2
DATABASE_URI_4=mongodb+srv://sihemar872_db_user:m0sFeAWexzrAqvMW@cluster0.5bkummz.mongodb.net/?appName=Cluster0
DATABASE_NAME_4=SPIDEY_FILE_STORAGE_2

# Database 5 - File Storage 3
DATABASE_URI_5=mongodb+srv://bawes77719_db_user:4nZaZZmNR2gxbkSP@cluster0.p1qnxox.mongodb.net/?appName=Cluster0
DATABASE_NAME_5=SPIDEY_FILE_STORAGE_3
```

## Usage Examples

### 1. Using Multi-Database Manager

```python
from database.multi_db_manager import multi_db_manager

# Get specific database
user_db = multi_db_manager.get_database("user_data")
file_storage_1 = multi_db_manager.get_database("file_storage_1")
file_storage_2 = multi_db_manager.get_database("file_storage_2")
file_storage_3 = multi_db_manager.get_database("file_storage_3")

# Test connections
connections = await multi_db_manager.test_connections()
print(connections)

# Get database statistics
stats = await multi_db_manager.get_database_stats()
print(stats)
```

### 2. Using Database Router

```python
from database.db_router import db_router

# Route data to appropriate database
user_collection = db_router.route_user_data("users")
file_storage_1_collection = db_router.route_file_storage_1("files")
file_storage_2_collection = db_router.route_file_storage_2("files")
file_storage_3_collection = db_router.route_file_storage_3("files")

# Or use convenience functions
from database.db_router import get_user_collection, get_file_storage_1_collection

users = get_user_collection("users")
files_1 = get_file_storage_1_collection("files")
```

### 3. File Storage System

```python
from database.file_storage_manager import (
    store_database_file,
    store_backup_file,
    store_archive_file,
    retrieve_file_by_id,
    get_file_list,
    delete_file_by_id
)

# Store different types of files
file_id_1 = await store_database_file("backup.json", file_content, {"version": "1.0"})
file_id_2 = await store_backup_file("user_data.json", file_content, {"type": "incremental"})
file_id_3 = await store_archive_file("old_logs.json", file_content, {"compressed": True})

# Retrieve files
file_data = await retrieve_file_by_id(file_id_1)
file_list = await get_file_list("database")  # Filter by type

# Delete files
success = await delete_file_by_id(file_id_1)
```

### 4. Legacy Compatibility

The existing database classes have been updated to use the multi-database system while maintaining backward compatibility:

```python
from database.users_chats_db import db
from database.config_db import mdb

# These will automatically use the appropriate database
user_count = await db.total_users_count()
group_count = await db.total_chat_count()
```

## Data Organization

### User Data (Database 2)
- User profiles and settings
- User points and premium status
- User verification data
- User requests and preferences
- User miscellaneous data

### File Storage 1 (Database 3)
- Database files and backups
- Media files and uploads
- Primary file storage
- Active database files

### File Storage 2 (Database 4)
- Backup files and archives
- Document files
- Secondary file storage
- Incremental backups

### File Storage 3 (Database 5)
- Archive files and logs
- Old/compressed files
- Tertiary file storage
- Long-term archives

### URL Data (Database 1)
- URL shortening data
- Link redirects
- URL analytics
- Shortener configurations

## Testing

Run the test script to verify all database connections:

```bash
python test_multi_db.py
```

This will test:
- Database connections
- Database router functionality
- Legacy compatibility
- Data operations

## Benefits

1. **Better Performance**: Data is distributed across multiple databases
2. **Improved Organization**: Related data is grouped together
3. **Scalability**: Each database can be scaled independently
4. **Backup Strategy**: Different backup schedules for different data types
5. **Security**: Sensitive data can be isolated in separate databases
6. **Maintenance**: Easier to maintain and debug specific data types

## Fallback System

If any database connection fails, the system automatically falls back to the main database to ensure the bot continues to function. This provides high availability and reliability.

## Monitoring

Use the following methods to monitor database health:

```python
# Test all connections
connections = await multi_db_manager.test_connections()

# Get database statistics
stats = await multi_db_manager.get_database_stats()

# Get router status
router_status = db_router.get_all_databases_status()
```

## Troubleshooting

1. **Connection Issues**: Check if all database URLs are correct and accessible
2. **Permission Issues**: Ensure database users have proper permissions
3. **Network Issues**: Check network connectivity to MongoDB clusters
4. **Fallback**: The system will automatically use the main database if multi-db fails

## Migration

The system is designed to work with existing code without changes. All existing database operations will continue to work while benefiting from the new multi-database architecture.

## Support

If you encounter any issues:
1. Check the test script output
2. Verify database connections
3. Check logs for specific error messages
4. Ensure all environment variables are set correctly
