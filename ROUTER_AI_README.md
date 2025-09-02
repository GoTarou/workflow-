# Router AI Integration for Document Workflow System

This document explains how to use the Router AI integration that has been added to your document workflow system.

## Overview

Router AI has been integrated into your document workflow system to provide intelligent document analysis capabilities. The integration includes:

- **Document Analysis**: Comprehensive analysis of documents using AI
- **Text Extraction**: Extract text content from various document formats
- **Document Summarization**: Generate summaries of varying lengths
- **Document Classification**: Automatically categorize documents by type
- **Message Routing**: Intelligently route employee messages to correct departments

## Features

### 1. Quick Analysis
Performs a comprehensive analysis of documents including:
- Text extraction
- Document classification
- Summary generation
- General analysis

### 2. Text Extraction
Extracts text content while preserving formatting and extracting tables.

### 3. Document Summarization
Generates summaries in three lengths:
- **Short**: Brief overview
- **Medium**: Balanced summary (default)
- **Long**: Detailed summary

### 4. Document Classification
Automatically categorizes documents into:
- Legal
- Financial
- Technical
- Medical
- General

### 5. Message Routing (NEW!)
Intelligently routes employee messages to the correct department using the company automation assistant prompt:
- **HR**: Leave requests, salary, payroll, benefits, vacation
- **Sales**: Customer orders, leads, deals, invoices
- **Facilities**: Building issues, repairs, maintenance, office supplies
- **IT**: Technical issues, login problems, software requests, hardware issues
- **Other**: General inquiries that don't fit the above categories

## API Endpoints

The following API endpoints have been added to your Flask application:

### POST `/api/ai/analyze/<doc_id>`
Analyzes a document with specified analysis type.

**Request Body:**
```json
{
    "analysis_type": "general"
}
```

### POST `/api/ai/extract/<doc_id>`
Extracts text from a document.

### POST `/api/ai/summarize/<doc_id>`
Generates a summary of a document.

**Request Body:**
```json
{
    "summary_length": "medium"
}
```

### POST `/api/ai/classify/<doc_id>`
Classifies a document.

### POST `/api/ai/quick-analysis/<doc_id>`
Performs comprehensive analysis (recommended for most use cases).

### POST `/api/ai/route-message` (NEW!)
Routes employee messages to the correct department.

**Request Body:**
```json
{
    "message": "I need to request vacation time for next week"
}
```

**Response:**
```json
{
    "success": true,
    "routing_result": {
        "department": "HR",
        "employee": null,
        "dates": "next week",
        "details": "Employee request related to HR matters",
        "raw_message": "I need to request vacation time for next week"
    }
}
```

## Usage in the UI

### Document Preview Page
When viewing a document in preview mode, you'll see two AI sections in the sidebar:

#### AI Analysis Section
1. **Quick Analysis** - Comprehensive analysis
2. **Extract Text** - Extract text content
3. **Summarize** - Generate document summary
4. **Classify** - Categorize document

#### Message Routing Section (NEW!)
1. **Message Input** - Enter employee messages
2. **Route Message** - Automatically route to correct department
3. **Routing Results** - View department assignment and extracted information

### How to Use Message Routing
1. Navigate to any document in your workflow system
2. Click on the document to view it
3. Click the "Preview" button
4. In the right sidebar, scroll down to the "Message Routing" section
5. Enter an employee message in the text area
6. Click "Route Message" to see the AI's routing decision
7. Results will show the assigned department and extracted details

## Company Automation Assistant Prompt

The AI system now uses a specialized prompt that defines its role as a company automation assistant:

```
You are a company automation assistant.  
Your job is to read employee messages and route them to the correct department.  

Step 1: Identify the department based on message content. Possible departments:  
- HR (leave requests, salary, payroll, benefits, vacation)  
- Sales (customer orders, leads, deals, invoices)  
- Facilities (building issues, repairs, maintenance, office supplies)  
- IT (technical issues, login problems, software requests, hardware issues)  
- Other (if none of the above clearly fit)

Step 2: Extract important information:
- employee name (if mentioned)
- relevant dates (if any)
- reason or description of the request
- original message

Step 3: Return the result in structured JSON:
{
   "department": "HR | Sales | Facilities | IT | Other",
   "employee": "Name if given, else null",
   "dates": "Any dates mentioned, else null",
   "details": "Reason/description in plain text",
   "raw_message": "Original message"
}
```

This prompt ensures the AI understands:
- Its specific role and responsibilities
- The department categories and their criteria
- What information to extract from messages
- The expected output format

## Configuration

### API Key
The Router AI API key is configured in `router_ai_config.py`:

```python
self.api_key = "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"
```

**Important**: In production, move this to environment variables for security.

### Base URL
The default Router AI API base URL is:
```python
self.base_url = "https://api.router.ai"
```

### Company Assistant Prompt
The prompt is automatically configured and cannot be modified without changing the code. It's designed to be:
- Clear and specific about the AI's role
- Comprehensive in covering all department categories
- Structured to ensure consistent output format

## Dependencies

The following packages have been added to `requirements.txt`:
- `requests==2.31.0`

## Testing

Run the test scripts to verify the integration:

### Test Message Routing
```bash
python test_message_routing.py
```

### Test General Router AI Functions
```bash
python test_router_ai.py
```

### Run Demo
```bash
python demo_router_ai.py
```

These tests will verify:
- Configuration loading
- API key validation
- Document analysis functions
- Message routing functionality
- Company assistant prompt integration

## Error Handling

The system includes comprehensive error handling:
- API request failures
- File not found errors
- Network connectivity issues
- Invalid document formats
- Empty or invalid messages
- Routing failures

Errors are displayed to users in the UI with helpful messages.

## Security

- All AI analysis endpoints require user authentication
- API keys are stored securely (move to environment variables in production)
- File access is restricted to authenticated users
- Message routing is logged for audit purposes

## Performance

- AI analysis results are cached temporarily
- Results auto-hide after 30 seconds to keep the UI clean
- Error messages auto-hide after 10 seconds
- Message routing is optimized for quick response times

## Troubleshooting

### Common Issues

1. **"API request failed" errors**
   - Check your internet connection
   - Verify the API key is correct
   - Ensure the Router AI service is available

2. **"Document file not found" errors**
   - Verify the document exists in the uploads folder
   - Check file permissions

3. **"Analysis failed" errors**
   - Check the document format is supported
   - Verify the file isn't corrupted

4. **"Message routing failed" errors**
   - Ensure the message is not empty
   - Check the message format is valid
   - Verify the AI prompt is properly configured

### Debug Mode
Enable debug logging by checking the browser console for detailed error messages.

## Future Enhancements

Potential improvements for the Router AI integration:
- Result caching and persistence
- Batch document processing
- Custom analysis templates
- Integration with workflow approval processes
- Export analysis results to reports
- Enhanced message routing with machine learning
- Integration with ticketing systems
- Automated workflow creation based on message content

## Support

For issues with the Router AI integration:
1. Check the browser console for error messages
2. Run the test scripts to verify configuration
3. Check the Flask application logs
4. Verify your Router AI API key and service status
5. Test message routing with the provided test script

## API Documentation

For detailed Router AI API documentation, visit:
- Router AI Official Documentation: [https://docs.router.ai](https://docs.router.ai)
- API Reference: [https://api.router.ai/docs](https://api.router.ai/docs)
