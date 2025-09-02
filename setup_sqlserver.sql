-- SQL Server Setup Script for Document Workflow System
-- Run this script in SQL Server Management Studio (SSMS) to set up the database

USE master;
GO

-- Create the database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'WorkflowDB')
BEGIN
    CREATE DATABASE WorkflowDB;
    PRINT 'Database WorkflowDB created successfully.';
END
ELSE
BEGIN
    PRINT 'Database WorkflowDB already exists.';
END
GO

-- Use the new database
USE WorkflowDB;
GO

-- Create the users table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[users] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [username] NVARCHAR(80) NOT NULL UNIQUE,
        [email] NVARCHAR(120) NOT NULL UNIQUE,
        [password_hash] NVARCHAR(120) NOT NULL,
        [role] NVARCHAR(20) DEFAULT 'user',
        [department] NVARCHAR(50) NULL,
        [created_at] DATETIME2 DEFAULT GETUTCDATE()
    );
    PRINT 'Table users created successfully.';
END
ELSE
BEGIN
    PRINT 'Table users already exists.';
END
GO

-- Create the documents table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[documents]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[documents] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [title] NVARCHAR(200) NOT NULL,
        [description] NTEXT NULL,
        [filename] NVARCHAR(255) NULL,
        [file_path] NVARCHAR(500) NULL,
        [status] NVARCHAR(20) DEFAULT 'pending',
        [priority] NVARCHAR(20) DEFAULT 'normal',
        [category] NVARCHAR(50) NULL,
        [submitter_id] INT NOT NULL,
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [updated_at] DATETIME2 DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_documents_users] FOREIGN KEY ([submitter_id]) REFERENCES [users]([id])
    );
    PRINT 'Table documents created successfully.';
END
ELSE
BEGIN
    PRINT 'Table documents already exists.';
END
GO

-- Create the workflow_steps table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[workflow_steps]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[workflow_steps] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [document_id] INT NOT NULL,
        [step_order] INT NOT NULL,
        [approver_id] INT NOT NULL,
        [status] NVARCHAR(20) DEFAULT 'pending',
        [comments] NTEXT NULL,
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        [completed_at] DATETIME2 NULL,
        CONSTRAINT [FK_workflow_steps_documents] FOREIGN KEY ([document_id]) REFERENCES [documents]([id]),
        CONSTRAINT [FK_workflow_steps_users] FOREIGN KEY ([approver_id]) REFERENCES [users]([id])
    );
    PRINT 'Table workflow_steps created successfully.';
END
ELSE
BEGIN
    PRINT 'Table workflow_steps already exists.';
END
GO

-- Create the approvals table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[approvals]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[approvals] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [document_id] INT NOT NULL,
        [approver_id] INT NOT NULL,
        [action] NVARCHAR(20) NOT NULL,
        [comments] NTEXT NULL,
        [created_at] DATETIME2 DEFAULT GETUTCDATE(),
        CONSTRAINT [FK_approvals_documents] FOREIGN KEY ([document_id]) REFERENCES [documents]([id]),
        CONSTRAINT [FK_approvals_users] FOREIGN KEY ([approver_id]) REFERENCES [users]([id])
    );
    PRINT 'Table approvals created successfully.';
END
ELSE
BEGIN
    PRINT 'Table approvals already exists.';
END
GO

-- Create indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_documents_submitter_id')
BEGIN
    CREATE INDEX [IX_documents_submitter_id] ON [documents]([submitter_id]);
    PRINT 'Index IX_documents_submitter_id created successfully.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_documents_status')
BEGIN
    CREATE INDEX [IX_documents_status] ON [documents]([status]);
    PRINT 'Index IX_documents_status created successfully.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_workflow_steps_document_id')
BEGIN
    CREATE INDEX [IX_workflow_steps_document_id] ON [workflow_steps]([document_id]);
    PRINT 'Index IX_workflow_steps_document_id created successfully.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_workflow_steps_approver_id')
BEGIN
    CREATE INDEX [IX_workflow_steps_approver_id] ON [workflow_steps]([approver_id]);
    PRINT 'Index IX_workflow_steps_approver_id created successfully.';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_approvals_document_id')
BEGIN
    CREATE INDEX [IX_approvals_document_id] ON [approvals]([document_id]);
    PRINT 'Index IX_approvals_document_id created successfully.';
END

-- Create sample users (optional - you can also create them through the application)
IF NOT EXISTS (SELECT * FROM [users] WHERE username = 'admin')
BEGIN
    INSERT INTO [users] (username, email, password_hash, role, department)
    VALUES ('admin', 'admin@company.com', 'pbkdf2:sha256:600000$your_hash_here', 'admin', 'IT');
    PRINT 'Sample admin user created.';
END

-- Verify the setup
SELECT 
    'Database Setup Complete' as Status,
    COUNT(*) as TotalTables
FROM sys.tables 
WHERE name IN ('users', 'documents', 'workflow_steps', 'approvals');

PRINT 'SQL Server setup completed successfully!';
PRINT 'You can now run the Python application.';
GO
