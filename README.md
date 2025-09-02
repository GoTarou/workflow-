# Document Workflow System

A modern, web-based document approval workflow system built with Python Flask and Microsoft SQL Server. This system automates the process of document submission, routing, and approval through configurable workflow steps.

## Features

### 🔐 User Management
- **Role-based access control**: Admin, Approver, and User roles
- **Department organization**: Users can be organized by departments
- **Secure authentication**: Password hashing and session management

### 📄 Document Management
- **File uploads**: Support for PDF, DOC, DOCX, TXT, JPG, PNG files
- **Metadata tracking**: Title, description, category, priority, and status
- **Version control**: Track creation and update timestamps

### 🔄 Workflow Automation
- **Multi-step approval**: Configurable approval sequences
- **Automatic routing**: Documents are automatically sent to approvers
- **Status tracking**: Real-time workflow progress monitoring
- **Approval actions**: Approve, reject, or add comments

### 📊 Dashboard & Analytics
- **Role-based views**: Different dashboards for different user types
- **Statistics cards**: Document counts by status and priority
- **Timeline visualization**: Visual workflow step tracking
- **Approval history**: Complete audit trail of all actions

### 🎨 Modern UI/UX
- **Responsive design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Modern, clean interface components
- **Font Awesome icons**: Professional iconography
- **Interactive elements**: Hover effects and smooth transitions

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   (SQL Server)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### Required Software
- **Python 3.7 or higher**
- **Microsoft SQL Server** (2016 or later)
- **SQL Server Management Studio (SSMS)** (optional but recommended)
- **ODBC Driver for SQL Server**

### ODBC Driver Installation
Download and install the appropriate ODBC driver for your SQL Server version:
- **SQL Server 2019+**: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **SQL Server 2016**: [ODBC Driver 13 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd workflow
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure SQL Server Connection

#### Option A: Edit Configuration File
Open `sqlserver_config.py` and update the following values:
```python
# SQL Server Instance Details
SQL_SERVER = 'GOTARUO\\MSSQLSERVER01'  # Your SQL Server instance
SQL_DATABASE = 'WorkflowDB'  # Database name

# Authentication Method
USE_WINDOWS_AUTH = True  # Use Windows Authentication (recommended)
# USE_WINDOWS_AUTH = False  # Use SQL Server Authentication
# SQL_USERNAME = 'sa'  # SQL Server username
# SQL_PASSWORD = 'your_password'  # SQL Server password
```

#### Option B: Environment Variables
Create a `.env` file in the root directory:
```env
SQL_SERVER=GOTARUO\\MSSQLSERVER01
SQL_DATABASE=WorkflowDB
USE_WINDOWS_AUTH=True
SQL_USERNAME=
SQL_PASSWORD=
```

### 5. Set Up SQL Server Database

#### Using SQL Server Management Studio (SSMS):
1. Open SSMS and connect to your SQL Server instance
2. Open the `setup_sqlserver.sql` file
3. Execute the script to create the database and tables
4. Verify the database `WorkflowDB` was created successfully

#### Using Command Line:
```bash
# Connect to SQL Server and run the setup script
sqlcmd -S "GOTARUO\MSSQLSERVER01" -i setup_sqlserver.sql
```

### 6. Initialize the Application
```bash
# Initialize database and create sample data
flask init-db
```

### 7. Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## SQL Server Configuration Details

### Connection String Format
The system automatically generates connection strings based on your configuration:

**Windows Authentication:**
```
mssql+pyodbc://GOTARUO\MSSQLSERVER01/WorkflowDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Server Authentication:**
```
mssql+pyodbc://username:password@GOTARUO\MSSQLSERVER01/WorkflowDB?driver=ODBC+Driver+17+for+SQL+Server
```

### Database Schema
The system creates the following tables:
- **`users`**: User accounts and roles
- **`documents`**: Document metadata and files
- **`workflow_steps`**: Approval workflow steps
- **`approvals`**: Approval history and comments

### Performance Optimization
The setup script includes:
- **Indexes** on frequently queried columns
- **Foreign key constraints** for data integrity
- **Proper data types** for optimal storage

## Default User Accounts

The system comes with pre-configured demo accounts:

| Username | Password | Role | Department |
|----------|----------|------|------------|
| `admin` | `admin123` | Administrator | IT |
| `approver1` | `approver123` | Approver | HR |
| `approver2` | `approver123` | Approver | Finance |
| `user1` | `user123` | User | Sales |

## Troubleshooting

### Common SQL Server Issues

1. **Connection Errors**
   - Verify SQL Server is running
   - Check instance name spelling (including backslashes)
   - Ensure ODBC driver is installed
   - Verify Windows Authentication is enabled

2. **Authentication Issues**
   - For Windows Authentication: Ensure your Windows account has SQL Server access
   - For SQL Server Authentication: Verify username/password and that SA account is enabled

3. **Database Not Found**
   - Run the `setup_sqlserver.sql` script first
   - Check database name spelling in configuration

4. **Permission Errors**
   - Ensure your SQL Server account has CREATE DATABASE permission
   - Check that the account can create tables and indexes

### ODBC Driver Issues
```bash
# Check available ODBC drivers
odbcinst -q -d

# Test connection using pyodbc
python -c "import pyodbc; print(pyodbc.drivers())"
```

### Connection Testing
```python
# Test connection in Python
import pyodbc
conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=GOTARUO\\MSSQLSERVER01;DATABASE=WorkflowDB;Trusted_Connection=yes;"
conn = pyodbc.connect(conn_str)
print("Connection successful!")
conn.close()
```

## Configuration Options

### SQL Server Settings
- **Connection Pooling**: Configure pool size and overflow in `sqlserver_config.py`
- **Timeout Settings**: Adjust connection and command timeouts
- **Driver Selection**: Choose between different ODBC driver versions

### Security Considerations
- **Windows Authentication**: Recommended for production (more secure)
- **SQL Server Authentication**: Use only if Windows Authentication is not available
- **Connection Encryption**: Enable in SQL Server for production environments

## Migration from SQLite

If you're migrating from the SQLite version:

1. **Backup existing data** from SQLite database
2. **Set up SQL Server** using the provided scripts
3. **Update configuration** to use SQL Server
4. **Recreate users** (passwords cannot be migrated due to hashing)
5. **Import documents** if needed

## Performance Tuning

### SQL Server Optimization
- **Enable Query Store** for performance monitoring
- **Configure Memory Settings** based on server capacity
- **Regular Maintenance** with SQL Server Agent jobs
- **Backup Strategy** for production environments

### Application Optimization
- **Connection Pooling** for better performance
- **Query Optimization** with proper indexes
- **Caching** for frequently accessed data

## Support

For SQL Server specific issues:
1. Check SQL Server error logs
2. Verify connection strings and authentication
3. Test connectivity using SSMS or sqlcmd
4. Review ODBC driver installation

---

**Built with ❤️ using Flask, Bootstrap, and Microsoft SQL Server**
