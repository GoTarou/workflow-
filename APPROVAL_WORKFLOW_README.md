# Approval Workflow System

A comprehensive approval workflow system integrated with Router AI for intelligent request routing and multi-level approval processes.

## 🎯 Overview

The Approval Workflow System automatically routes employee requests to the correct department using AI-powered analysis, then manages a two-tier approval process:

1. **Department Approval**: Department-specific approvers review and approve/reject requests
2. **Admin Approval**: Final approval from administrators for department-approved requests
3. **AI Routing**: Intelligent request classification using Router AI with company automation assistant prompts

## 🏗️ System Architecture

### Database Models

- **User**: Users with roles (admin, approver, user)
- **DepartmentApprover**: Links departments to their approvers
- **Request**: Employee requests with status tracking
- **RequestApproval**: Approval history and comments

### Workflow States

```
pending → department_approved → admin_approved → completed
    ↓
rejected (can happen at any level)
```

## 🚀 Quick Start

### 1. Setup Database

```bash
python setup_approval_workflow.py
```

This will create:
- All necessary database tables
- Sample users with different roles
- Department approvers for each department

### 2. Run Application

```bash
python app.py
```

### 3. Login Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`
- Role: Admin (full access)

**Department Approvers:**
- HR Manager: `hr_manager` / `hr123`
- Sales Director: `sales_director` / `sales123`
- Facilities Manager: `facilities_manager` / `facilities123`
- IT Manager: `it_manager` / `it123`

**Regular Employees:**
- Employee 1: `employee1` / `emp123`
- Employee 2: `employee2` / `emp123`

## 🔄 How It Works

### 1. Request Submission

1. Employee submits a request through the "My Requests" page
2. Router AI analyzes the message content using company automation assistant prompts
3. AI determines the appropriate department (HR, Sales, Facilities, IT, Other)
4. Request is automatically routed to the department's assigned approver

### 2. Department Approval

1. Department approver receives notification of pending request
2. Approver reviews request details and approval history
3. Approver can:
   - **Approve**: Request moves to admin approval level
   - **Reject**: Request is rejected and returned to employee
   - **Add Comments**: Provide feedback or reasoning

### 3. Admin Approval

1. Admin reviews department-approved requests
2. Admin can:
   - **Approve**: Request is fully approved and completed
   - **Reject**: Request is rejected and returned to employee
   - **Add Comments**: Provide final feedback

### 4. AI-Powered Routing

The system uses Router AI with this prompt:

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

## 📱 User Interface

### For Employees

- **My Requests**: Submit new requests and view request history
- **Request Status**: Track approval progress
- **Notifications**: See when requests are approved/rejected

### For Department Approvers

- **Approvals**: Review pending requests for their department
- **Request Details**: View full request information and history
- **Approval Actions**: Approve, reject, or add comments

### For Admins

- **All Approvals**: Review all requests across departments
- **Manage Approvers**: Assign/remove department approvers
- **System Overview**: Monitor workflow statistics

## 🔧 API Endpoints

### Request Management

- `GET /api/requests` - Get requests (filtered by user role)
- `GET /api/requests/<id>` - Get specific request details
- `POST /api/requests/<id>/approve` - Approve/reject request

### Department Approvers

- `GET /api/department-approvers` - Get all department approvers
- `POST /api/department-approvers` - Create new department approver
- `DELETE /api/department-approvers/<id>` - Remove department approver

### AI Routing

- `POST /api/ai/route-message` - Route message using AI analysis

## 🎨 Customization

### Adding New Departments

1. Update the AI prompt in `router_ai_config.py`
2. Add department options in the UI templates
3. Create corresponding department approver assignments

### Modifying Approval Levels

The system supports custom approval workflows by modifying the `Request` model and approval logic in `app.py`.

### Custom AI Prompts

Modify the `company_assistant_prompt` in `router_ai_config.py` to change how the AI routes requests.

## 📊 Monitoring and Analytics

### Request Statistics

- Pending requests count
- Department approval rates
- Average approval time
- Rejection reasons analysis

### User Activity

- Request submission patterns
- Approver response times
- Department workload distribution

## 🔒 Security Features

- **Role-based Access Control**: Users only see what they're authorized to see
- **Audit Trail**: Complete history of all approval actions
- **Input Validation**: Sanitized request inputs
- **Session Management**: Secure user authentication

## 🚨 Error Handling

- **Graceful Degradation**: System continues working even if AI routing fails
- **User Feedback**: Clear error messages for failed operations
- **Fallback Routing**: Manual department selection if AI fails
- **Logging**: Comprehensive error logging for debugging

## 🔮 Future Enhancements

### Planned Features

- **Email Notifications**: Automatic email alerts for status changes
- **Mobile App**: Native mobile application for approvals
- **Advanced Analytics**: Machine learning insights on approval patterns
- **Integration**: Connect with external HR/ERP systems
- **Workflow Templates**: Pre-defined approval workflows for common requests

### AI Improvements

- **Learning**: AI learns from approval patterns to improve routing
- **Priority Detection**: Automatic priority assignment based on content
- **Sentiment Analysis**: Understand request urgency from message tone
- **Multi-language Support**: Route requests in different languages

## 🐛 Troubleshooting

### Common Issues

1. **AI Routing Fails**
   - Check Router AI API configuration
   - Verify API key is valid
   - Check network connectivity

2. **Approval Not Working**
   - Verify user has correct role permissions
   - Check if department approver is assigned
   - Ensure request status allows approval

3. **Database Errors**
   - Run database migrations
   - Check database connection
   - Verify table structure

### Debug Mode

Enable debug mode in `app.py` for detailed error logging:

```python
app.run(debug=True)
```

## 📚 API Documentation

### Request Object Structure

```json
{
  "id": 1,
  "title": "Request: Vacation time for next week",
  "message": "Hi, I need to request vacation time for next week...",
  "department": "HR",
  "status": "pending",
  "priority": "normal",
  "submitter": "employee1",
  "department_approver": "hr_manager",
  "admin_approver": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "approvals": []
}
```

### Approval Object Structure

```json
{
  "id": 1,
  "request_id": 1,
  "approver_id": 2,
  "approval_level": "department",
  "action": "approve",
  "comments": "Approved - standard vacation request",
  "created_at": "2024-01-15T11:00:00Z"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section above
2. Review the API documentation
3. Check the issue tracker
4. Contact the development team

---

**🎉 Congratulations!** You now have a fully functional approval workflow system with AI-powered request routing and multi-level approval processes.
