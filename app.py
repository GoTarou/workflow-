from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json

# Import SQL Server configuration
from sqlserver_config import get_flask_sqlalchemy_uri
# Import Router AI configuration
from router_ai_config import router_ai
# Import ML Workflow Progression
from ml_workflow_progression import MLWorkflowProgression
# Import Linear Regression Workflow
from linear_regression_workflow import LinearRegressionWorkflow
# Import Department Detection
from department_detection import DepartmentDetection

app = Flask(__name__, static_folder='static')
# Load secret key from environment for public repositories. Do NOT hardcode secrets.
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-me-in-prod')

# SQL Server Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = get_flask_sqlalchemy_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize ML Workflow Progression
ml_workflow_system = MLWorkflowProgression()
# Initialize Linear Regression Workflow
linear_regression_system = LinearRegressionWorkflow()
# Initialize Department Detection
department_detection_system = DepartmentDetection()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Add debugging to login manager
@login_manager.unauthorized_handler
def unauthorized():
    print(f"🚫 Unauthorized access attempt - Session: {dict(session)}")
    print(f"🚫 Current user: {current_user}")
    return redirect(url_for('login'))

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, approver, user
    department = db.Column(db.String(50))
    _is_active = db.Column('is_active', db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Flask-Login is_active property
    @property
    def is_active(self):
        return self._is_active if self._is_active is not None else True
    
    # Relationships
    submitted_documents = db.relationship('Document', backref='submitter', lazy=True, foreign_keys='Document.submitter_id')
    approvals = db.relationship('Approval', backref='approver', lazy=True)
    submitted_requests = db.relationship('Request', backref='request_submitter', lazy=True, foreign_keys='Request.submitter_id')
    request_approvals = db.relationship('RequestApproval', backref='request_approver', lazy=True)
    department_approver_roles = db.relationship('DepartmentApprover', backref='department_approver', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, archived
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    category = db.Column(db.String(50))
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow_steps = db.relationship('WorkflowStep', backref='document', lazy=True, order_by='WorkflowStep.step_order')
    approvals = db.relationship('Approval', backref='document', lazy=True)

class WorkflowStep(db.Model):
    __tablename__ = 'workflow_steps'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    approver = db.relationship('User', backref='workflow_steps')

class Approval(db.Model):
    __tablename__ = 'approvals'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # approve, reject, comment
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# New Models for Approval Workflow System
class DepartmentApprover(db.Model):
    __tablename__ = 'department_approvers'
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(50), nullable=False)  # HR, Sales, Facilities, IT, Other
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one approver per department
    __table_args__ = (db.UniqueConstraint('department', 'approver_id', name='unique_department_approver'),)

class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(50), nullable=False)  # HR, Sales, Facilities, IT, Other
    status = db.Column(db.String(20), default='pending')  # pending, general_approved, department_approved, admin_approved, rejected, completed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admin_approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submitter = db.relationship('User', foreign_keys=[submitter_id])
    department_approver = db.relationship('User', foreign_keys=[department_approver_id])
    admin_approver = db.relationship('User', foreign_keys=[admin_approver_id])
    approvals = db.relationship('RequestApproval', backref='request_obj', lazy=True, order_by='RequestApproval.created_at')

class RequestApproval(db.Model):
    __tablename__ = 'request_approvals'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approval_level = db.Column(db.String(20), nullable=False)  # department, admin
    action = db.Column(db.String(20), nullable=False)  # approve, reject, comment
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    approver = db.relationship('User', backref='approvals_given')

class WorkflowFlowDisplay(db.Model):
    __tablename__ = 'workflow_flow_display'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    step_name = db.Column(db.String(50), nullable=False)  # User, General Approver, Department Approver, Admin
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    request = db.relationship('Request', backref='workflow_flow')
    user = db.relationship('User', backref='workflow_flow_steps')

@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(int(user_id))
        print(f"🔍 Loading user with ID {user_id}: {user.username if user else 'Not found'}")
        if user:
            print(f"✅ User loaded successfully: {user.username} (ID: {user.id})")
        return user
    except Exception as e:
        print(f"❌ Error loading user {user_id}: {str(e)}")
        return None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('requests_page'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt - Username: {username}, Password length: {len(password) if password else 0}")
        
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user is not None}")
        
        if user and check_password_hash(user.password_hash, password):
            print(f"Password check passed for user: {username}")
            
            # Check if is_active field exists and handle None values
            if hasattr(user, 'is_active'):
                if user.is_active is False:  # Explicitly check for False
                    print(f"User {username} is not active")
                    flash('Account is deactivated. Please contact administrator.')
                    return render_template('login.html')
            # If is_active field doesn't exist or is None/True, allow login
            
            # Login the user
            login_user(user, remember=True)
            print(f"User logged in successfully: {username}")
            print(f"User role: {user.role}")
            print(f"User ID: {user.id}")
            print(f"Session after login: {dict(session)}")
            print(f"Redirecting to: {url_for('requests_page')}")
            
            return redirect(url_for('requests_page'))
        else:
            print(f"Login failed for user: {username}")
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/requests')
@login_required
def requests_page():
    """Requests page"""
    print(f"✅ User {current_user.username} successfully accessed requests page")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user ID: {current_user.id}")
    print(f"Session data: {dict(session)}")
    print(f"🔍 Flask-Login current_user: {current_user}")
    print(f"🔍 Flask-Login is_authenticated: {current_user.is_authenticated}")
    print(f"🔍 Flask-Login is_anonymous: {current_user.is_anonymous}")
    return render_template('requests.html')

@app.route('/requests/<int:request_id>')
@login_required
def view_request(request_id):
    """View specific request"""
    return render_template('view_request.html', request_id=request_id)

@app.route('/approvals')
@login_required
def approvals_page():
    """Approvals page for approvers and admins"""
    if current_user.role not in ['admin', 'approver']:
        flash('Access denied. Approver role required.', 'error')
        return redirect(url_for('requests_page'))
    
    return render_template('approvals.html')

@app.route('/manage-approvers')
@login_required
def manage_approvers():
    """Manage department approvers (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('requests_page'))
    
    return render_template('manage_approvers.html')

@app.route('/analytics')
@login_required
def analytics_dashboard():
    """Analytics dashboard (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied. Admin role required.', 'error')
        return redirect(url_for('requests_page'))
    
    return render_template('analytics.html')

@app.route('/document/new', methods=['GET', 'POST'])
@login_required
def new_document():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        priority = request.form.get('priority')
        
        # Handle file upload
        file = request.files.get('file')
        filename = None
        file_path = None
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        
        # Create document
        document = Document(
            title=title,
            description=description,
            category=category,
            priority=priority,
            filename=filename,
            file_path=file_path,
            submitter_id=current_user.id
        )
        db.session.add(document)
        db.session.commit()
        
        # Create workflow steps: 2 approvers + 1 admin final approval
        approvers = User.query.filter_by(role='approver').limit(2).all()
        admin = User.query.filter_by(role='admin').first()
        
        # Add approver steps
        for i, approver in enumerate(approvers):
            step = WorkflowStep(
                document_id=document.id,
                step_order=i + 1,
                approver_id=approver.id
            )
            db.session.add(step)
        
        # Add admin as final approver (step 3)
        if admin:
            admin_step = WorkflowStep(
                document_id=document.id,
                step_order=3,
                approver_id=admin.id
            )
            db.session.add(admin_step)
        
        db.session.commit()
        flash('Document submitted successfully!')
        return redirect(url_for('requests_page'))
    
    return render_template('new_document.html')

@app.route('/document/<int:doc_id>')
@login_required
def view_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    workflow_steps = WorkflowStep.query.filter_by(document_id=doc_id).order_by(WorkflowStep.step_order).all()
    approvals = Approval.query.filter_by(document_id=doc_id).order_by(Approval.created_at).all()
    
    # Check if current user can approve this document
    can_approve = False
    if current_user.role in ['admin', 'approver']:
        for step in workflow_steps:
            if step.approver_id == current_user.id and step.status == 'pending':
                can_approve = True
                break
    
    return render_template('view_document.html', 
                         document=document, 
                         workflow_steps=workflow_steps, 
                         approvals=approvals,
                         can_approve=can_approve)

@app.route('/document/<int:doc_id>/approve', methods=['POST'])
@login_required
def approve_document(doc_id):
    if current_user.role not in ['admin', 'approver']:
        flash('You do not have permission to approve documents')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    action = request.form.get('action')  # approve, reject, comment
    comments = request.form.get('comments', '')
    
    # Check if user is in the workflow for this document
    workflow_step = WorkflowStep.query.filter_by(
        document_id=doc_id,
        approver_id=current_user.id,
        status='pending'
    ).first()
    
    if not workflow_step:
        flash('You are not authorized to approve this document')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    # Create approval record
    approval = Approval(
        document_id=doc_id,
        approver_id=current_user.id,
        action=action,
        comments=comments
    )
    db.session.add(approval)
    
    # Update workflow step
    workflow_step.status = action
    workflow_step.comments = comments
    workflow_step.completed_at = datetime.utcnow()
    
    # Update document status if all steps are complete
    pending_steps = WorkflowStep.query.filter_by(
        document_id=doc_id,
        status='pending'
    ).count()
    
    if pending_steps == 0:
        # Check if any steps were rejected
        rejected_steps = WorkflowStep.query.filter_by(
            document_id=doc_id,
            status='rejected'
        ).count()
        
        if rejected_steps > 0:
            document = Document.query.get(doc_id)
            document.status = 'rejected'
        else:
            document = Document.query.get(doc_id)
            document.status = 'approved'
    
    db.session.commit()
    flash(f'Document {action}ed successfully!')
    return redirect(url_for('view_document', doc_id=doc_id))

@app.route('/document/<int:doc_id>/archive', methods=['POST'])
@login_required
def archive_document(doc_id):
    if current_user.role != 'admin':
        flash('Only administrators can archive documents')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    document = Document.query.get_or_404(doc_id)
    document.status = 'archived'
    db.session.commit()
    
    flash('Document archived successfully!')
    return redirect(url_for('requests_page'))

@app.route('/document/<int:doc_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    if current_user.role != 'admin':
        flash('Only administrators can edit documents')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    document = Document.query.get_or_404(doc_id)
    
    if request.method == 'POST':
        document.title = request.form.get('title')
        document.description = request.form.get('description')
        document.category = request.form.get('category')
        document.priority = request.form.get('priority')
        document.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Document updated successfully!')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    return render_template('edit_document.html', document=document)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files with proper security"""
    from werkzeug.utils import secure_filename
    import os
    
    # Security check - ensure filename is safe
    safe_filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    if os.path.exists(file_path):
        # Determine content type based on file extension
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        
        if content_type is None:
            content_type = 'application/octet-stream'
        
        return send_file(file_path, mimetype=content_type)
    else:
        abort(404)

@app.route('/document/<int:doc_id>/preview')
@login_required
def preview_document(doc_id):
    """Document preview page with highlighting tools"""
    document = Document.query.get_or_404(doc_id)
    
    if not document.filename:
        flash('No document attached to preview')
        return redirect(url_for('view_document', doc_id=doc_id))
    
    # Get file extension to determine preview type
    file_ext = os.path.splitext(document.filename)[1].lower()
    
    # Determine if file can be previewed
    previewable_extensions = {
        '.pdf': 'pdf',
        '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', '.bmp': 'image',
        '.txt': 'text', '.md': 'text', '.csv': 'text',
        '.doc': 'office', '.docx': 'office', '.xls': 'office', '.xlsx': 'office'
    }
    
    preview_type = previewable_extensions.get(file_ext, 'download')
    
    # For text files, read the content
    text_content = ""
    if preview_type == 'text' and document.file_path:
        try:
            with open(document.file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            text_content = f"Error reading file: {str(e)}"
    
    return render_template('preview_document.html', 
                         document=document, 
                         preview_type=preview_type,
                         file_ext=file_ext,
                         text_content=text_content)

@app.route('/api/documents')
@login_required
def api_documents():
    documents = Document.query.all()
    return jsonify([{
        'id': doc.id,
        'title': doc.title,
        'status': doc.status,
        'priority': doc.priority,
        'category': doc.category,
        'submitter': doc.submitter.username,
        'created_at': doc.created_at.isoformat(),
        'updated_at': doc.updated_at.isoformat()
    } for doc in documents])

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('requests_page'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('requests_page'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('create_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('create_user.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            department=department
        )
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!')
        return redirect(url_for('admin_users'))
    
    return render_template('create_user.html')

# Initialize database and create sample data
@app.cli.command("init-db")
def init_db():
    db.create_all()
    
    # Clear existing department approvers only
    DepartmentApprover.query.delete()
    db.session.commit()
    
    # Don't delete old users for now - just create new ones
    print("Note: Keeping existing users to avoid foreign key conflicts")
    
    # Create sample users if they don't exist
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@company.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            department='IT'
        )
        db.session.add(admin)
    
    # Create new general approver
    if not User.query.filter_by(username='general_approver').first():
        general_approver = User(
            username='general_approver',
            email='general.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='General'
        )
        db.session.add(general_approver)
    
    # Create new department approvers
    if not User.query.filter_by(username='hr_approver').first():
        hr_approver = User(
            username='hr_approver',
            email='hr.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='HR'
        )
        db.session.add(hr_approver)
    
    if not User.query.filter_by(username='it_approver').first():
        it_approver = User(
            username='it_approver',
            email='it.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='IT'
        )
        db.session.add(it_approver)
    
    if not User.query.filter_by(username='finance_approver').first():
        finance_approver = User(
            username='finance_approver',
            email='finance.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='Finance'
        )
        db.session.add(finance_approver)
    
    if not User.query.filter_by(username='facilities_approver').first():
        facilities_approver = User(
            username='facilities_approver',
            email='facilities.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='Facilities'
        )
        db.session.add(facilities_approver)
    
    if not User.query.filter_by(username='sales_approver').first():
        sales_approver = User(
            username='sales_approver',
            email='sales.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='Sales'
        )
        db.session.add(sales_approver)
    
    if not User.query.filter_by(username='legal_approver').first():
        legal_approver = User(
            username='legal_approver',
            email='legal.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='Legal'
        )
        db.session.add(legal_approver)
    
    if not User.query.filter_by(username='operations_approver').first():
        operations_approver = User(
            username='operations_approver',
            email='operations.approver@company.com',
            password_hash=generate_password_hash('approver123'),
            role='approver',
            department='Operations'
        )
        db.session.add(operations_approver)
    
    if not User.query.filter_by(username='user1').first():
        user1 = User(
            username='user1',
            email='user1@company.com',
            password_hash=generate_password_hash('user123'),
            role='user',
            department='Sales'
        )
        db.session.add(user1)
    
    db.session.commit()
    
    # Create department approvers mapping
    department_approvers = {
        'HR': 'hr_approver',
        'IT': 'it_approver',
        'Finance': 'finance_approver',
        'Facilities': 'facilities_approver',
        'Sales': 'sales_approver',
        'Legal': 'legal_approver',
        'Operations': 'operations_approver'
    }
    
    for department, username in department_approvers.items():
        user = User.query.filter_by(username=username).first()
        if user:
            dept_approver = DepartmentApprover(
                department=department,
                approver_id=user.id
            )
            db.session.add(dept_approver)
    
    db.session.commit()
    
    # Populate workflow flow display for existing requests
    print("Populating workflow flow display for existing requests...")
    existing_requests = Request.query.all()
    for req in existing_requests:
        # Check if workflow flow already exists for this request
        existing_flow = WorkflowFlowDisplay.query.filter_by(request_id=req.id).first()
        if not existing_flow:
            # Create workflow flow display records
            # Step 0: User (Submitter)
            submitter = User.query.get(req.submitter_id)
            if submitter:
                user_flow = WorkflowFlowDisplay(
                    request_id=req.id,
                    step_number=0,
                    step_name='User (Submitter)',
                    user_id=submitter.id,
                    username=submitter.username,
                    role='user',
                    department=submitter.department,
                    status='completed'
                )
                db.session.add(user_flow)
            
            # Step 1: General Approver
            general_approver = User.query.filter_by(username='general_approver').first()
            if general_approver:
                general_flow = WorkflowFlowDisplay(
                    request_id=req.id,
                    step_number=1,
                    step_name='General Approver',
                    user_id=general_approver.id,
                    username=general_approver.username,
                    role='general_approver',
                    department='General',
                    status='pending' if req.status == 'pending' else 'approved'
                )
                db.session.add(general_flow)
            
            # Step 2: Department Approver
            if req.department_approver_id:
                dept_user = User.query.get(req.department_approver_id)
                if dept_user:
                    dept_flow = WorkflowFlowDisplay(
                        request_id=req.id,
                        step_number=2,
                        step_name=f'{req.department} Department Approver',
                        user_id=dept_user.id,
                        username=dept_user.username,
                        role='department_approver',
                        department=req.department,
                        status='pending' if req.status in ['pending', 'general_approved'] else 'approved'
                    )
                    db.session.add(dept_flow)
            
            # Step 3: Admin Approver
            admin_approver = User.query.filter_by(role='admin').first()
            if admin_approver:
                admin_flow = WorkflowFlowDisplay(
                    request_id=req.id,
                    step_number=3,
                    step_name='Admin Approver',
                    user_id=admin_approver.id,
                    username=admin_approver.username,
                    role='admin',
                    department='Admin',
                    status='pending' if req.status in ['pending', 'general_approved', 'department_approved'] else 'approved'
                )
                db.session.add(admin_flow)
    
    db.session.commit()
    print("Workflow flow display populated for existing requests!")
    
    # Update workflow flow display statuses based on current request statuses
    print("Updating workflow flow display statuses...")
    for req in existing_requests:
        # Update general approver status
        general_flow = WorkflowFlowDisplay.query.filter_by(
            request_id=req.id,
            step_number=1,
            step_name='General Approver'
        ).first()
        if general_flow:
            if req.status in ['general_approved', 'department_approved', 'admin_approved']:
                general_flow.status = 'approved'
            elif req.status == 'rejected':
                general_flow.status = 'rejected'
        
        # Update department approver status
        dept_flow = WorkflowFlowDisplay.query.filter_by(
            request_id=req.id,
            step_number=2
        ).first()
        if dept_flow:
            if req.status in ['department_approved', 'admin_approved']:
                dept_flow.status = 'approved'
            elif req.status == 'rejected':
                dept_flow.status = 'rejected'
        
        # Update admin approver status
        admin_flow = WorkflowFlowDisplay.query.filter_by(
            request_id=req.id,
            step_number=3,
            step_name='Admin Approver'
        ).first()
        if admin_flow:
            if req.status == 'admin_approved':
                admin_flow.status = 'approved'
            elif req.status == 'rejected':
                admin_flow.status = 'rejected'
    
    db.session.commit()
    print("Workflow flow display statuses updated!")
    
    print("Database initialized with new workflow system!")
    print("New users created:")
    print("- admin (admin123)")
    print("- general_approver (approver123)")
    print("- hr_approver (approver123)")
    print("- it_approver (approver123)")
    print("- finance_approver (approver123)")
    print("- facilities_approver (approver123)")
    print("- sales_approver (approver123)")
    print("- legal_approver (approver123)")
    print("- operations_approver (approver123)")
    print("- user1 (user123)")

# Router AI Integration Routes
@app.route('/api/ai/analyze/<int:doc_id>', methods=['POST'])
@login_required
def ai_analyze_document(doc_id):
    """Analyze document using Router AI"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({"error": "Document file not found"}), 404
        
        # Get analysis type from request
        analysis_type = request.json.get('analysis_type', 'general')
        
        # Perform analysis using Router AI
        result = router_ai.analyze_document(document.file_path, analysis_type)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "analysis_type": analysis_type,
            "results": result
        })
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/ai/extract/<int:doc_id>', methods=['POST'])
@login_required
def ai_extract_text(doc_id):
    """Extract text from document using Router AI"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({"error": "Document file not found"}), 404
        
        # Extract text using Router AI
        result = router_ai.extract_text(document.file_path)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "extracted_text": result
        })
    except Exception as e:
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500

@app.route('/api/ai/summarize/<int:doc_id>', methods=['POST'])
@login_required
def ai_summarize_document(doc_id):
    """Summarize document using Router AI"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({"error": "Document file not found"}), 404
        
        # Get summary length from request
        summary_length = request.json.get('summary_length', 'medium')
        
        # Generate summary using Router AI
        result = router_ai.summarize_document(document.file_path, summary_length)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "summary_length": summary_length,
            "summary": result
        })
    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

@app.route('/api/ai/classify/<int:doc_id>', methods=['POST'])
@login_required
def ai_classify_document(doc_id):
    """Classify document using Router AI"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({"error": "Document file not found"}), 404
        
        # Classify document using Router AI
        result = router_ai.classify_document(document.file_path)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "classification": result
        })
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500

@app.route('/api/ai/quick-analysis/<int:doc_id>', methods=['POST'])
@login_required
def ai_quick_analysis(doc_id):
    """Perform quick analysis using Router AI"""
    try:
        document = Document.query.get_or_404(doc_id)
        
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({"error": "Document file not found"}), 404
        
        # Perform quick analysis using Router AI
        result = router_ai.quick_analysis(document.file_path)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "document_id": doc_id,
            "analysis_results": result
        })
    except Exception as e:
        return jsonify({"error": f"Quick analysis failed: {str(e)}"}), 500

@app.route('/api/ai/route-message', methods=['POST'])
@login_required
def ai_route_message():
    """Route employee message to correct department using Router AI"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Route message using Router AI
        routing_result = router_ai.route_message(message)
        
        if "error" in routing_result:
            return jsonify({"error": routing_result["error"]}), 400
        
        # Return only the routing results, don't create request yet
        return jsonify({
            "success": True,
            "routing_results": routing_result,
            "message": "Message analyzed successfully. Please confirm to submit request."
        })
        
    except Exception as e:
        return jsonify({"error": f"Message routing failed: {str(e)}"}), 500

@app.route('/api/requests/create', methods=['POST'])
@login_required
def create_request():
    """Create a new request after AI analysis confirmation"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        department = data.get('department')
        priority = data.get('priority', 'normal')
        
        if not message or not department:
            return jsonify({"error": "Message and department are required"}), 400
        
        # Find the department approver
        department_approver = DepartmentApprover.query.filter_by(
            department=department,
            is_active=True
        ).first()
        
        if not department_approver:
            return jsonify({
                "error": f"No approver found for {department} department"
            }), 404
        
        # Create the request title
        request_title = f"Request: {message[:50]}{'...' if len(message) > 50 else ''}"
        
        # Create the request
        new_request = Request(
            title=request_title,
            message=message,
            department=department,
            submitter_id=current_user.id,
            department_approver_id=department_approver.approver_id,
            priority=priority
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        # Create the full 3-step workflow: General Approver → Department Approver → Admin Approver
        
        # Step 1: General Approver
        general_approver = User.query.filter_by(username='general_approver').first()
        if general_approver:
            general_approval = RequestApproval(
                request_id=new_request.id,
                approver_id=general_approver.id,
                approval_level='general',
                action='pending',
                comments='Request submitted and routed to General Approver (Step 1)'
            )
            db.session.add(general_approval)
        
        # Step 2: Department Approver
        department_approval = RequestApproval(
            request_id=new_request.id,
            approver_id=department_approver.approver_id,
            approval_level='department',
            action='pending',
            comments=f'Request routed to {department} Department Approver (Step 2)'
        )
        db.session.add(department_approval)
        
        # Step 3: Admin Approver
        admin_approver = User.query.filter_by(role='admin').first()
        if admin_approver:
            admin_approval = RequestApproval(
                request_id=new_request.id,
                approver_id=admin_approver.id,
                approval_level='admin',
                action='pending',
                comments='Request routed to Admin Approver (Step 3)'
            )
            db.session.add(admin_approval)
        
        # Create workflow flow display records for easy viewing
        # Step 0: User (Submitter)
        user_flow = WorkflowFlowDisplay(
            request_id=new_request.id,
            step_number=0,
            step_name='User (Submitter)',
            user_id=current_user.id,
            username=current_user.username,
            role='user',
            department=current_user.department,
            status='completed'
        )
        db.session.add(user_flow)
        
        # Step 1: General Approver
        if general_approver:
            general_flow = WorkflowFlowDisplay(
                request_id=new_request.id,
                step_number=1,
                step_name='General Approver',
                user_id=general_approver.id,
                username=general_approver.username,
                role='general_approver',
                department='General',
                status='pending'
            )
            db.session.add(general_flow)
        
        # Step 2: Department Approver
        dept_user = User.query.get(department_approver.approver_id)
        if dept_user:
            dept_flow = WorkflowFlowDisplay(
                request_id=new_request.id,
                step_number=2,
                step_name=f'{department} Department Approver',
                user_id=dept_user.id,
                username=dept_user.username,
                role='department_approver',
                department=department,
                status='pending'
            )
            db.session.add(dept_flow)
        
        # Step 3: Admin Approver
        if admin_approver:
            admin_flow = WorkflowFlowDisplay(
                request_id=new_request.id,
                step_number=3,
                step_name='Admin Approver',
                user_id=admin_approver.id,
                username=admin_approver.username,
                role='admin',
                department='Admin',
                status='pending'
            )
            db.session.add(admin_flow)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "request_id": new_request.id,
            "message": "Request created and routed successfully",
            "department_approver": {
                "id": department_approver.approver_id,
                "name": User.query.get(department_approver.approver_id).username
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Request creation failed: {str(e)}"}), 500

@app.route('/api/requests/create-workflow', methods=['POST'])
@login_required
def create_workflow_request():
    """Create a new request with custom workflow steps"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        priority = data.get('priority', 'normal')
        workflow_steps = data.get('workflow_steps', [])
        
        if not title or not message:
            return jsonify({"error": "Title and message are required"}), 400
        
        if not workflow_steps or len(workflow_steps) == 0:
            return jsonify({"error": "At least one workflow step is required"}), 400
        
        # Find the actual department that needs approval (skip General Approver and Admin steps)
        actual_department = None
        for step in workflow_steps:
            if step['department'] not in ['General Approver', 'Admin']:
                actual_department = step['department']
                break
        
        if not actual_department:
            return jsonify({
                "error": "No department specified in workflow steps"
            }), 400
        
        # Find the department approver for the actual department
        department_approver = DepartmentApprover.query.filter_by(
            department=actual_department,
            is_active=True
        ).first()
        
        if not department_approver:
            return jsonify({
                "error": f"No approver found for {actual_department} department"
            }), 404
        
        # Create the request
        new_request = Request(
            title=title,
            message=message,
            department=actual_department,
            submitter_id=current_user.id,
            department_approver_id=department_approver.approver_id,
            priority=priority
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        # Create workflow steps as RequestApproval records
        for i, step_data in enumerate(workflow_steps):
            department = step_data['department']
            step_order = step_data['stepNumber']
            
            # Handle different step types
            if department == "General Approver":
                # General approver step - find the general approver
                step_approver = User.query.filter_by(username='general_approver').first()
                approval_level = 'general'
            elif department == "Admin":
                # Admin step - find admin user
                step_approver = User.query.filter_by(role='admin').first()
                approval_level = 'admin'
            else:
                # Department-specific step - find department approver
                step_approver = DepartmentApprover.query.filter_by(
                    department=department,
                    is_active=True
                ).first()
                approval_level = 'department'
            
            if step_approver:
                # Create approval record for this workflow step
                approval = RequestApproval(
                    request_id=new_request.id,
                    approver_id=step_approver.id if hasattr(step_approver, 'id') else step_approver.approver_id,
                    approval_level=approval_level,
                    action='pending',
                    comments=f'Request submitted and routed to {department} (Step {step_order})'
                )
                db.session.add(approval)
        
        # Create workflow flow display records for easy viewing
        # Step 0: User (Submitter)
        user_flow = WorkflowFlowDisplay(
            request_id=new_request.id,
            step_number=0,
            step_name='User (Submitter)',
            user_id=current_user.id,
            username=current_user.username,
            role='user',
            department=current_user.department,
            status='completed'
        )
        db.session.add(user_flow)
        
        # Create flow records for each workflow step
        for i, step_data in enumerate(workflow_steps):
            department = step_data['department']
            step_order = step_data['stepNumber']
            
            if department == "General Approver":
                step_approver = User.query.filter_by(username='general_approver').first()
                if step_approver:
                    flow_record = WorkflowFlowDisplay(
                        request_id=new_request.id,
                        step_number=step_order,
                        step_name=department,
                        user_id=step_approver.id,
                        username=step_approver.username,
                        role='general_approver',
                        department='General',
                        status='pending'
                    )
                    db.session.add(flow_record)
            elif department == "Admin":
                step_approver = User.query.filter_by(role='admin').first()
                if step_approver:
                    flow_record = WorkflowFlowDisplay(
                        request_id=new_request.id,
                        step_number=step_order,
                        step_name=department,
                        user_id=step_approver.id,
                        username=step_approver.username,
                        role='admin',
                        department='Admin',
                        status='pending'
                    )
                    db.session.add(flow_record)
            else:
                # Department-specific step
                step_approver = DepartmentApprover.query.filter_by(
                    department=department,
                    is_active=True
                ).first()
                if step_approver:
                    dept_user = User.query.get(step_approver.approver_id)
                    if dept_user:
                        flow_record = WorkflowFlowDisplay(
                            request_id=new_request.id,
                            step_number=step_order,
                            step_name=f'{department} Department Approver',
                            user_id=dept_user.id,
                            username=dept_user.username,
                            role='department_approver',
                            department=department,
                            status='pending'
                        )
                        db.session.add(flow_record)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "request_id": new_request.id,
            "message": "Workflow request created successfully",
            "workflow_steps": len(workflow_steps),
            "actual_department": actual_department,
            "department_approver": {
                "id": department_approver.approver_id,
                "name": User.query.get(department_approver.approver_id).username
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Workflow request creation failed: {str(e)}"}), 500

# ML Workflow Progression API Routes
@app.route('/api/ml/train', methods=['POST'])
@login_required
def train_ml_workflow():
    """Train the ML workflow progression model with historical data"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get all approval data for training
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for training"}), 400
        
        # Prepare training data
        training_data = []
        for approval in approvals:
            # Get request details
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            # Get workflow step details
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                training_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',  # Can be enhanced later
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.updated_at.isoformat() if hasattr(approval, 'updated_at') else approval.created_at.isoformat()
                })
        
        # Train the model
        training_result = ml_workflow_system.train_model(training_data)
        
        if "error" in training_result:
            return jsonify({"error": training_result["error"]}), 400
        
        return jsonify({
            "success": True,
            "message": "ML Workflow Model trained successfully",
            "training_metrics": training_result,
            "training_samples": len(training_data)
        })
        
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500

@app.route('/api/ml/predict', methods=['POST'])
@login_required
def predict_next_department():
    """Predict the next optimal department for workflow progression"""
    try:
        data = request.get_json()
        current_department = data.get('current_department')
        priority = data.get('priority', 'normal')
        step_order = data.get('step_order', 1)
        request_type = data.get('request_type', 'general')
        
        if not current_department:
            return jsonify({"error": "Current department is required"}), 400
        
        # Make prediction
        prediction = ml_workflow_system.predict_next_department(
            current_department, priority, step_order, request_type
        )
        
        if "error" in prediction:
            return jsonify({"error": prediction["error"]}), 400
        
        return jsonify({
            "success": True,
            "prediction": prediction
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/ml/suggest-workflow', methods=['POST'])
@login_required
def suggest_ml_workflow():
    """Get ML-suggested workflow based on request type and priority"""
    try:
        data = request.get_json()
        request_type = data.get('request_type', 'general')
        priority = data.get('priority', 'normal')
        max_steps = data.get('max_steps', 5)
        
        # Get ML workflow suggestion
        suggestion = ml_workflow_system.suggest_workflow(
            request_type, priority, max_steps
        )
        
        if "error" in suggestion:
            return jsonify({"error": suggestion["error"]}), 400
        
        return jsonify({
            "success": True,
            "suggested_workflow": suggestion
        })
        
    except Exception as e:
        return jsonify({"error": f"Workflow suggestion failed: {str(e)}"}), 500

@app.route('/api/ml/analyze-patterns', methods=['GET'])
@login_required
def analyze_workflow_patterns():
    """Analyze workflow patterns and provide insights"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get all approval data for analysis
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for analysis"}), 400
        
        # Prepare analysis data
        analysis_data = []
        for approval in approvals:
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                analysis_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.updated_at.isoformat() if hasattr(approval, 'updated_at') else approval.created_at.isoformat()
                })
        
        # Analyze patterns
        analysis_result = ml_workflow_system.analyze_workflow_patterns(analysis_data)
        
        if "error" in analysis_result:
            return jsonify({"error": analysis_result["error"]}), 400
        
        return jsonify({
            "success": True,
            "pattern_analysis": analysis_result
        })
        
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/ml/export-data', methods=['POST'])
@login_required
def export_training_data():
    """Export training data to CSV for external analysis"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        data = request.get_json()
        filename = data.get('filename')
        
        # Get all approval data
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for export"}), 400
        
        # Prepare export data
        export_data = []
        for approval in approvals:
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                export_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.created_at.isoformat()  # RequestApproval doesn't have updated_at
                })
        
        # Export data
        export_path = ml_workflow_system.export_training_data(export_data, filename)
        
        return jsonify({
            "success": True,
            "message": "Training data exported successfully",
            "export_path": export_path,
            "exported_records": len(export_data)
        })
        
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.route('/api/ml/model-status', methods=['GET'])
@login_required
def get_model_status():
    """Get the current status of the ML workflow model"""
    try:
        model_loaded = ml_workflow_system.workflow_model is not None
        
        status_info = {
            "model_loaded": model_loaded,
            "model_path": ml_workflow_system.model_path,
            "last_training": "Unknown"  # Can be enhanced to track training timestamps
        }
        
        if model_loaded:
            status_info["model_type"] = type(ml_workflow_system.workflow_model).__name__
            status_info["feature_count"] = len(ml_workflow_system.workflow_model.feature_importances_) if hasattr(ml_workflow_system.workflow_model, 'feature_importances_') else "Unknown"
        
        return jsonify({
            "success": True,
            "model_status": status_info
        })
        
    except Exception as e:
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

# Linear Regression API Routes
@app.route('/api/linear-regression/train-approval-time', methods=['POST'])
@login_required
def train_approval_time_model():
    """Train linear regression model to predict approval times"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get all approval data for training
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for training"}), 400
        
        # Prepare training data
        training_data = []
        for approval in approvals:
            # Get request details
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            # Get workflow step details
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                training_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',  # Can be enhanced later
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.updated_at.isoformat() if hasattr(approval, 'updated_at') else approval.created_at.isoformat()
                })
        
        # Train the approval time model
        training_result = linear_regression_system.train_approval_time_model(training_data)
        
        if "error" in training_result:
            return jsonify({"error": training_result["error"]}), 400
        
        return jsonify({
            "success": True,
            "message": "Approval Time Model trained successfully",
            "training_result": training_result
        })
        
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500

@app.route('/api/linear-regression/train-success-rate', methods=['POST'])
@login_required
def train_success_rate_model():
    """Train linear regression model to predict success rates"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get all approval data for training
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for training"}), 400
        
        # Prepare training data
        training_data = []
        for approval in approvals:
            # Get request details
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            # Get workflow step details
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                training_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',  # Can be enhanced later
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.updated_at.isoformat() if hasattr(approval, 'updated_at') else approval.created_at.isoformat()
                })
        
        # Train the success rate model
        training_result = linear_regression_system.train_success_rate_model(training_data)
        
        if "error" in training_result:
            return jsonify({"error": training_result["error"]}), 400
        
        return jsonify({
            "success": True,
            "message": "Success Rate Model trained successfully",
            "training_result": training_result
        })
        
    except Exception as e:
        return jsonify({"error": f"Training failed: {str(e)}"}), 500

@app.route('/api/linear-regression/predict-approval-time', methods=['POST'])
@login_required
def predict_approval_time():
    """Predict approval time for a new request"""
    try:
        data = request.get_json()
        priority = data.get('priority', 'normal')
        num_steps = data.get('num_steps', 4)
        request_type = data.get('request_type', 'general')
        dept_complexity = data.get('dept_complexity', 3)
        day_of_week = data.get('day_of_week')
        time_of_day = data.get('time_of_day')
        
        # Make prediction
        prediction = linear_regression_system.predict_approval_time(
            priority, num_steps, request_type, dept_complexity, day_of_week, time_of_day
        )
        
        if "error" in prediction:
            return jsonify({"error": prediction["error"]}), 400
        
        return jsonify({
            "success": True,
            "prediction": prediction
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/linear-regression/predict-success-rate', methods=['POST'])
@login_required
def predict_success_rate():
    """Predict success rate for a new request"""
    try:
        data = request.get_json()
        priority = data.get('priority', 'normal')
        num_steps = data.get('num_steps', 4)
        request_type = data.get('request_type', 'general')
        dept_complexity = data.get('dept_complexity', 3)
        
        # Make prediction
        prediction = linear_regression_system.predict_success_rate(
            priority, num_steps, request_type, dept_complexity
        )
        
        if "error" in prediction:
            return jsonify({"error": prediction["error"]}), 400
        
        return jsonify({
            "success": True,
            "prediction": prediction
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/linear-regression/feature-importance', methods=['GET'])
@login_required
def get_feature_importance():
    """Get feature importance for linear regression models"""
    try:
        model_name = request.args.get('model', 'approval_time')
        
        # Get feature importance
        importance = linear_regression_system.analyze_feature_importance(model_name)
        
        if "error" in importance:
            return jsonify({"error": importance["error"]}), 400
        
        return jsonify({
            "success": True,
            "feature_importance": importance
        })
        
    except Exception as e:
        return jsonify({"error": f"Feature importance analysis failed: {str(e)}"}), 500

@app.route('/api/linear-regression/generate-insights', methods=['POST'])
@login_required
def generate_linear_regression_insights():
    """Generate comprehensive insights from linear regression analysis"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Get all approval data for analysis
        approvals = RequestApproval.query.all()
        
        if not approvals:
            return jsonify({"error": "No approval data available for analysis"}), 400
        
        # Prepare analysis data
        analysis_data = []
        for approval in approvals:
            request_obj = Request.query.get(approval.request_id)
            if not request_obj:
                continue
            
            workflow_step = WorkflowStep.query.filter_by(
                document_id=approval.request_id,
                approver_id=approval.approver_id
            ).first()
            
            if workflow_step:
                analysis_data.append({
                    'request_id': approval.request_id,
                    'department': request_obj.department,
                    'priority': request_obj.priority,
                    'step_order': workflow_step.step_order,
                    'request_type': 'general',
                    'status': approval.action,
                    'created_at': approval.created_at.isoformat(),
                    'updated_at': approval.updated_at.isoformat() if hasattr(approval, 'updated_at') else approval.created_at.isoformat()
                })
        
        # Generate insights
        insights = linear_regression_system.generate_insights(analysis_data)
        
        return jsonify({
            "success": True,
            "insights": insights
        })
        
    except Exception as e:
        return jsonify({"error": f"Insight generation failed: {str(e)}"}), 500

@app.route('/api/ai/suggest-workflow', methods=['POST'])
@login_required
def ai_suggest_workflow():
    """AI-powered workflow suggestion based on request description"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Request description is required"}), 400
        
        # Determine the appropriate department based on request type
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['off', 'vacation', 'leave', 'sick', 'ill', 'holiday', 'work leave', 'time off', 'personal leave']):
            # HR-related request
            department = "HR"
        elif any(word in message_lower for word in ['laptop', 'computer', 'hardware', 'software', 'system', 'access', 'password', 'email', 'network', 'server', 'database']):
            # IT-related request
            department = "IT"
        elif any(word in message_lower for word in ['budget', 'expense', 'purchase', 'cost', 'money', 'financial', 'invoice', 'payment', 'reimbursement', 'accounting']):
            # Finance-related request
            department = "Finance"
        elif any(word in message_lower for word in ['facility', 'building', 'maintenance', 'repair', 'space', 'office', 'room', 'equipment', 'cleaning', 'security']):
            # Facilities-related request
            department = "Facilities"
        elif any(word in message_lower for word in ['sales', 'deal', 'client', 'contract', 'proposal', 'quotation', 'customer', 'lead', 'opportunity']):
            # Sales-related request
            department = "Sales"
        elif any(word in message_lower for word in ['legal', 'compliance', 'contract', 'regulation', 'policy', 'agreement', 'terms', 'liability', 'risk']):
            # Legal-related request
            department = "Legal"
        elif any(word in message_lower for word in ['operation', 'process', 'procedure', 'workflow', 'efficiency', 'productivity', 'quality', 'standard']):
            # Operations-related request
            department = "Operations"
        else:
            # General request - default to HR
            department = "HR"
        
        # New 3-step workflow: General Approver → Department Approver → Admin Approver
        workflow_steps = [
            {
                "department": "General Approver", 
                "step": 1, 
                "reason": "Initial review and approval by general approver",
                "role": "general_approver"
            },
            {
                "department": department, 
                "step": 2, 
                "reason": f"Department-specific approval by {department} department approver",
                "role": "department_approver"
            },
            {
                "department": "Admin", 
                "step": 3, 
                "reason": "Final administrative approval",
                "role": "admin"
            }
        ]
        
        return jsonify({
            "success": True,
            "workflow_steps": workflow_steps,
            "request_type": "standard_3step",
            "confidence": "high",
            "workflow_pattern": "General Approver → Department Approver → Admin Approver",
            "detected_department": department
        })
        
    except Exception as e:
        return jsonify({"error": f"Workflow suggestion failed: {str(e)}"}), 500

# Approval Workflow API Routes
@app.route('/api/requests', methods=['GET'])
@login_required
def get_requests():
    """Get requests based on user role and permissions"""
    try:
        if current_user.role == 'admin':
            # Admin sees all requests
            requests = Request.query.order_by(Request.created_at.desc()).all()
        elif current_user.role == 'approver':
            # Approver sees requests for their departments and requests they need to approve
            if current_user.username == 'general_approver':
                # General approver sees all pending requests
                requests = Request.query.filter_by(status='pending').order_by(Request.created_at.desc()).all()
            else:
                # Department approver sees requests for their department
                department_approver = DepartmentApprover.query.filter_by(
                    approver_id=current_user.id,
                    is_active=True
                ).first()
                
                if department_approver:
                    requests = Request.query.filter(
                        (Request.department == department_approver.department) |
                        (Request.department_approver_id == current_user.id)
                    ).order_by(Request.created_at.desc()).all()
                else:
                    requests = []
        else:
            # Regular users see only their own requests
            requests = Request.query.filter_by(submitter_id=current_user.id).order_by(Request.created_at.desc()).all()
        
        requests_data = []
        for req in requests:
            # Get workflow steps for this request
            workflow_steps = []
            for approval in req.approvals:
                approver = User.query.get(approval.approver_id)
                workflow_steps.append({
                    'step': len(workflow_steps) + 1,
                    'department': approval.approval_level.title(),
                    'approver': approver.username if approver else 'Unknown',
                    'status': approval.action
                })
            
            requests_data.append({
                'id': req.id,
                'title': req.title,
                'message': req.message,
                'department': req.department,
                'status': req.status,
                'priority': req.priority,
                'submitter': req.submitter.username,
                'department_approver': req.department_approver.username if req.department_approver else None,
                'created_at': req.created_at.isoformat(),
                'updated_at': req.updated_at.isoformat(),
                'workflow_steps': workflow_steps
            })
        
        return jsonify({
            "success": True,
            "requests": requests_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch requests: {str(e)}"}), 500

@app.route('/api/requests/<int:request_id>', methods=['GET'])
@login_required
def get_request(request_id):
    """Get specific request details"""
    try:
        request_obj = Request.query.get_or_404(request_id)
        
        # Check permissions
        if current_user.role != 'admin' and request_obj.submitter_id != current_user.id:
            # General approver can view any request
            if current_user.username == 'general_approver':
                pass  # Allow access
            else:
                # Check if user is a department approver for this request
                department_approver = DepartmentApprover.query.filter_by(
                    approver_id=current_user.id,
                    department=request_obj.department,
                    is_active=True
                ).first()
                
                if not department_approver:
                    return jsonify({"error": "Access denied"}), 403
        
        # Get approval history and workflow steps
        approvals = []
        workflow_steps = []
        
        for approval in request_obj.approvals:
            approver = User.query.get(approval.approver_id)
            approvals.append({
                'id': approval.id,
                'approver': approver.username if approver else 'Unknown',
                'approval_level': approval.approval_level,
                'action': approval.action,
                'comments': approval.comments,
                'created_at': approval.created_at.isoformat()
            })
            
            # Create workflow step information
            step_number = len(workflow_steps) + 1
            workflow_steps.append({
                'step': step_number,
                'department': approval.approval_level.title(),
                'approver': approver.username if approver else 'Unknown',
                'approver_id': approval.approver_id,
                'status': approval.action,
                'comments': approval.comments,
                'created_at': approval.created_at.isoformat()
            })
        
        request_data = {
            'id': request_obj.id,
            'title': request_obj.title,
            'message': request_obj.message,
            'department': request_obj.department,
            'status': request_obj.status,
            'priority': request_obj.priority,
            'submitter': request_obj.submitter.username,
            'department_approver': request_obj.department_approver.username if request_obj.department_approver else None,
            'admin_approver': request_obj.admin_approver.username if request_obj.admin_approver else None,
            'created_at': request_obj.created_at.isoformat(),
            'updated_at': request_obj.updated_at.isoformat(),
            'approvals': approvals,
            'workflow_steps': workflow_steps
        }
        
        return jsonify({
            "success": True,
            "request": request_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch request: {str(e)}"}), 500

@app.route('/api/requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_request(request_id):
    """Approve or reject a request"""
    try:
        request_obj = Request.query.get_or_404(request_id)
        data = request.get_json()
        action = data.get('action', 'approve')  # approve, reject
        comments = data.get('comments', '')
        
        # Check if user can approve this request
        can_approve = False
        approval_level = None
        
        if current_user.role == 'admin':
            can_approve = True
            approval_level = 'admin'
        elif current_user.username == 'general_approver':
            # General approver can approve any pending request
            if request_obj.status == 'pending':
                can_approve = True
                approval_level = 'general'
        else:
            # Department approver can approve requests for their department
            department_approver = DepartmentApprover.query.filter_by(
                approver_id=current_user.id,
                department=request_obj.department,
                is_active=True
            ).first()
            
            if department_approver and request_obj.status == 'general_approved':
                can_approve = True
                approval_level = 'department'
        
        if not can_approve:
            return jsonify({"error": "You are not authorized to approve this request"}), 403
        
        # Create approval record
        approval = RequestApproval(
            request_id=request_id,
            approver_id=current_user.id,
            approval_level=approval_level,
            action=action,
            comments=comments
        )
        
        db.session.add(approval)
        
        # Update request status
        if action == 'approve':
            if approval_level == 'general':
                request_obj.status = 'general_approved'
                # Update workflow flow display for general approval
                general_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=1,
                    step_name='General Approver'
                ).first()
                if general_flow:
                    general_flow.status = 'approved'
            elif approval_level == 'department':
                request_obj.status = 'department_approved'
                request_obj.department_approver_id = current_user.id
                # Update workflow flow display for department approval
                dept_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=2
                ).first()
                if dept_flow:
                    dept_flow.status = 'approved'
            elif approval_level == 'admin':
                request_obj.status = 'admin_approved'
                request_obj.admin_approver_id = current_user.id
                # Update workflow flow display for admin approval
                admin_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=3,
                    step_name='Admin Approver'
                ).first()
                if admin_flow:
                    admin_flow.status = 'approved'
        elif action == 'reject':
            request_obj.status = 'rejected'
            # Update workflow flow display for rejection
            if approval_level == 'general':
                general_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=1,
                    step_name='General Approver'
                ).first()
                if general_flow:
                    general_flow.status = 'rejected'
            elif approval_level == 'department':
                dept_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=2
                ).first()
                if dept_flow:
                    dept_flow.status = 'rejected'
            elif approval_level == 'admin':
                admin_flow = WorkflowFlowDisplay.query.filter_by(
                    request_id=request_id,
                    step_number=3,
                    step_name='Admin Approver'
                ).first()
                if admin_flow:
                    admin_flow.status = 'rejected'
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Request {action}d successfully",
            "new_status": request_obj.status
        })
        
    except Exception as e:
        return jsonify({"error": f"Approval failed: {str(e)}"}), 500

@app.route('/api/department-approvers', methods=['GET'])
@login_required
def get_department_approvers():
    """Get all department approvers (admin only)"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        approvers = DepartmentApprover.query.filter_by(is_active=True).all()
        approvers_data = []
        
        for approver in approvers:
            user = User.query.get(approver.approver_id)
            approvers_data.append({
                'id': approver.id,
                'department': approver.department,
                'approver_id': approver.approver_id,
                'approver_name': user.username,
                'approver_email': user.email,
                'is_active': approver.is_active,
                'created_at': approver.created_at.isoformat()
            })
        
        return jsonify({
            "success": True,
            "approvers": approvers_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch approvers: {str(e)}"}), 500

@app.route('/api/department-approvers', methods=['POST'])
@login_required
def create_department_approver():
    """Create a new department approver (admin only)"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        data = request.get_json()
        department = data.get('department')
        approver_id = data.get('approver_id')
        
        if not department or not approver_id:
            return jsonify({"error": "Department and approver_id are required"}), 400
        
        # Check if approver exists
        user = User.query.get(approver_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if department already has an approver
        existing_approver = DepartmentApprover.query.filter_by(
            department=department,
            is_active=True
        ).first()
        
        if existing_approver:
            return jsonify({"error": f"Department {department} already has an approver"}), 400
        
        # Create new approver
        new_approver = DepartmentApprover(
            department=department,
            approver_id=approver_id
        )
        
        db.session.add(new_approver)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Department approver created successfully for {department}",
            "approver_id": new_approver.id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to create approver: {str(e)}"}), 500

@app.route('/api/department-approvers/<int:approver_id>', methods=['DELETE'])
@login_required
def delete_department_approver(approver_id):
    """Delete a department approver (admin only)"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        approver = DepartmentApprover.query.get_or_404(approver_id)
        approver.is_active = False
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Department approver deactivated successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete approver: {str(e)}"}), 500

@app.route('/api/requests/<int:request_id>', methods=['DELETE'])
@login_required
def delete_request(request_id):
    """Delete a request (admin only)"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        request_obj = Request.query.get_or_404(request_id)
        
        # Delete all related approvals first
        RequestApproval.query.filter_by(request_id=request_id).delete()
        
        # Delete the request
        db.session.delete(request_obj)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Request deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete request: {str(e)}"}), 500

@app.route('/api/user-info')
@login_required
def get_user_info():
    """Get current user information"""
    try:
        return jsonify({
            "success": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role,
                "department": current_user.department
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get user info: {str(e)}"}), 500

@app.route('/api/analytics/dashboard')
@login_required
def get_analytics_dashboard():
    """Get comprehensive analytics data for dashboard"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied. Admin role required."}), 403
    
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Parse dates
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        # Build query filters
        query_filters = []
        if from_date:
            query_filters.append(Request.created_at >= from_date)
        if to_date:
            query_filters.append(Request.created_at <= to_date)
        
        # Get requests with filters
        requests_query = Request.query
        if query_filters:
            requests_query = requests_query.filter(*query_filters)
        
        all_requests = requests_query.all()
        
        # Calculate KPIs
        total_requests = len(all_requests)
        pending_requests = len([r for r in all_requests if r.status == 'pending'])
        
        # Calculate approval rate
        approved_requests = len([r for r in all_requests if r.status in ['general_approved', 'department_approved', 'admin_approved']])
        approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate average approval time
        avg_approval_time_hours = calculate_average_approval_time(all_requests)
        
        # Request volume trends (daily for last 30 days)
        request_volume_trends = calculate_request_volume_trends(all_requests, from_date, to_date)
        
        # Department distribution
        department_distribution = calculate_department_distribution(all_requests)
        
        # Approval time by department
        approval_time_by_department = calculate_approval_time_by_department(all_requests)
        
        # Top submitters
        top_submitters = calculate_top_submitters(all_requests)
        
        # Bottleneck analysis
        bottleneck_analysis = calculate_bottleneck_analysis(all_requests)
        
        # Department performance ranking
        department_performance = calculate_department_performance(all_requests)
        
        # Department metrics table
        department_metrics = calculate_department_metrics(all_requests)
        
        return jsonify({
            "success": True,
            "data": {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "approval_rate": approval_rate,
                "avg_approval_time_hours": avg_approval_time_hours,
                "request_volume_trends": request_volume_trends,
                "department_distribution": department_distribution,
                "approval_time_by_department": approval_time_by_department,
                "top_submitters": top_submitters,
                "bottleneck_analysis": bottleneck_analysis,
                "department_performance": department_performance,
                "department_metrics": department_metrics
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch analytics: {str(e)}"}), 500

# Analytics calculation functions
def calculate_average_approval_time(requests):
    """Calculate average approval time in hours"""
    total_time = 0
    count = 0
    
    for req in requests:
        if (hasattr(req, 'status') and req.status in ['general_approved', 'department_approved', 'admin_approved'] and 
            hasattr(req, 'updated_at') and req.updated_at):
            time_diff = req.updated_at - req.created_at
            total_time += time_diff.total_seconds() / 3600  # Convert to hours
            count += 1
    
    return total_time / count if count > 0 else 0

def calculate_request_volume_trends(requests, from_date, to_date):
    """Calculate daily request volume trends"""
    from collections import defaultdict
    import calendar
    
    # Default to last 30 days if no dates provided
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=30)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Generate date range
    date_range = []
    current_date = from_date
    while current_date <= to_date:
        date_range.append(current_date.date())
        current_date += timedelta(days=1)
    
    # Count requests by date
    daily_counts = defaultdict(int)
    for req in requests:
        if hasattr(req, 'created_at') and req.created_at:
            req_date = req.created_at.date()
            if req_date in date_range:
                daily_counts[req_date] += 1
    
    # Fill in missing dates with 0
    labels = []
    values = []
    for date in date_range:
        labels.append(date.strftime('%m/%d'))
        values.append(daily_counts[date])
    
    return {
        "labels": labels,
        "values": values
    }

def calculate_department_distribution(requests):
    """Calculate request distribution by department"""
    from collections import Counter
    
    dept_counts = Counter()
    for req in requests:
        if hasattr(req, 'department') and req.department:
            dept_counts[req.department] += 1
    
    return {
        "labels": list(dept_counts.keys()),
        "values": list(dept_counts.values())
    }

def calculate_approval_time_by_department(requests):
    """Calculate average approval time by department"""
    from collections import defaultdict
    
    dept_times = defaultdict(list)
    
    for req in requests:
        if (hasattr(req, 'status') and req.status in ['general_approved', 'department_approved', 'admin_approved'] and 
            hasattr(req, 'updated_at') and req.updated_at and 
            hasattr(req, 'department') and req.department):
            time_diff = req.updated_at - req.created_at
            hours = time_diff.total_seconds() / 3600
            dept_times[req.department].append(hours)
    
    # Calculate averages
    labels = []
    values = []
    for dept, times in dept_times.items():
        labels.append(dept)
        values.append(sum(times) / len(times))
    
    return {
        "labels": labels,
        "values": values
    }

def calculate_top_submitters(requests):
    """Calculate top request submitters"""
    from collections import Counter
    
    submitter_counts = Counter()
    for req in requests:
        if hasattr(req, 'submitter') and req.submitter:
            submitter_counts[req.submitter.username] += 1
    
    # Get top 10 submitters
    top_submitters = submitter_counts.most_common(10)
    
    return {
        "labels": [submitter for submitter, count in top_submitters],
        "values": [count for submitter, count in top_submitters]
    }

def calculate_bottleneck_analysis(requests):
    """Identify bottlenecks in the approval process"""
    from collections import defaultdict
    
    dept_bottlenecks = defaultdict(lambda: {"total_time": 0, "count": 0})
    
    for req in requests:
        if (hasattr(req, 'status') and req.status in ['general_approved', 'department_approved', 'admin_approved'] and 
            hasattr(req, 'updated_at') and req.updated_at and 
            hasattr(req, 'department') and req.department):
            time_diff = req.updated_at - req.created_at
            hours = time_diff.total_seconds() / 3600
            
            dept_bottlenecks[req.department]["total_time"] += hours
            dept_bottlenecks[req.department]["count"] += 1
    
    # Calculate averages and identify bottlenecks
    bottlenecks = []
    for dept, data in dept_bottlenecks.items():
        if data["count"] > 0:
            avg_time = data["total_time"] / data["count"]
            bottlenecks.append({
                "department": dept,
                "step_name": "Department Approval",
                "avg_time_hours": avg_time,
                "request_count": data["count"]
            })
    
    # Sort by average time (slowest first)
    bottlenecks.sort(key=lambda x: x["avg_time_hours"], reverse=True)
    
    return bottlenecks[:5]  # Top 5 bottlenecks

def calculate_department_performance(requests):
    """Calculate department performance ranking"""
    from collections import defaultdict
    
    dept_metrics = defaultdict(lambda: {"total_time": 0, "count": 0, "approved": 0})
    
    for req in requests:
        if (hasattr(req, 'status') and req.status in ['general_approved', 'department_approved', 'admin_approved'] and 
            hasattr(req, 'updated_at') and req.updated_at and 
            hasattr(req, 'department') and req.department):
            time_diff = req.updated_at - req.created_at
            hours = time_diff.total_seconds() / 3600
            
            dept_metrics[req.department]["total_time"] += hours
            dept_metrics[req.department]["count"] += 1
            dept_metrics[req.department]["approved"] += 1
        elif hasattr(req, 'status') and req.status == 'rejected' and hasattr(req, 'department') and req.department:
            dept_metrics[req.department]["count"] += 1
    
    # Calculate performance scores
    performance_data = []
    for dept, data in dept_metrics.items():
        if data["count"] > 0:
            avg_time = data["total_time"] / data["count"]
            approval_rate = (data["approved"] / data["count"]) * 100
            
            # Performance score: 0-10 (lower time and higher approval rate = better score)
            time_score = max(0, 10 - (avg_time / 24))  # 24 hours = 0 points
            approval_score = approval_rate / 10  # 100% = 10 points
            performance_score = (time_score + approval_score) / 2
            
            performance_data.append({
                "name": dept,
                "avg_time_hours": avg_time,
                "performance_score": performance_score
            })
    
    # Sort by performance score (highest first)
    performance_data.sort(key=lambda x: x["performance_score"], reverse=True)
    
    return performance_data

def calculate_department_metrics(requests):
    """Calculate comprehensive metrics for each department"""
    from collections import defaultdict
    
    dept_metrics = defaultdict(lambda: {
        "total_requests": 0,
        "approved_requests": 0,
        "pending_requests": 0,
        "rejected_requests": 0,
        "total_time": 0,
        "approved_count": 0
    })
    
    for req in requests:
        if hasattr(req, 'department') and req.department:
            dept_metrics[req.department]["total_requests"] += 1
            
            if hasattr(req, 'status'):
                if req.status == 'pending':
                    dept_metrics[req.department]["pending_requests"] += 1
                elif req.status in ['general_approved', 'department_approved', 'admin_approved']:
                    dept_metrics[req.department]["approved_requests"] += 1
                    if hasattr(req, 'updated_at') and req.updated_at:
                        time_diff = req.updated_at - req.created_at
                        hours = time_diff.total_seconds() / 3600
                        dept_metrics[req.department]["total_time"] += hours
                        dept_metrics[req.department]["approved_count"] += 1
                elif req.status == 'rejected':
                    dept_metrics[req.department]["rejected_requests"] += 1
    
    # Format metrics for display
    formatted_metrics = []
    for dept, data in dept_metrics.items():
        avg_approval_time = data["total_time"] / data["approved_count"] if data["approved_count"] > 0 else 0
        approval_rate = (data["approved_requests"] / data["total_requests"] * 100) if data["total_requests"] > 0 else 0
        
        # Calculate performance score
        time_score = max(0, 10 - (avg_approval_time / 24))
        approval_score = approval_rate / 10
        performance_score = (time_score + approval_score) / 2
        
        formatted_metrics.append({
            "name": dept,
            "total_requests": data["total_requests"],
            "avg_approval_time_hours": avg_approval_time,
            "approval_rate": approval_rate,
            "pending_count": data["pending_requests"],
            "performance_score": performance_score
        })
    
    # Sort by performance score
    formatted_metrics.sort(key=lambda x: x["performance_score"], reverse=True)
    
    return formatted_metrics

@app.route('/api/users')
@login_required
def get_users():
    """Get all users (admin only)"""
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'department': user.department,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            "success": True,
            "users": users_data
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500

# CSV Upload for ML Training
@app.route('/api/ml/upload-csv', methods=['POST'])
@login_required
def upload_csv_training_data():
    """Upload CSV file to train the ML workflow model"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            return jsonify({"error": "No CSV file uploaded"}), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        if not file.filename.lower().endswith('.csv'):
            return jsonify({"error": "File must be a CSV"}), 400
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        # Create temp file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'uploaded_training_data.csv')
        file.save(temp_path)
        
        # Read and validate CSV
        import pandas as pd
        try:
            df = pd.read_csv(temp_path)
            print(f"✅ CSV uploaded successfully! Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Validate required columns
            required_columns = ['phrase', 'department']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return jsonify({
                    "error": f"Missing required columns: {missing_columns}",
                    "uploaded_columns": list(df.columns),
                    "required_columns": required_columns
                }), 400
            
            # Convert DataFrame to training data format
            training_data = []
            for _, row in df.iterrows():
                training_data.append({
                    'phrase': str(row['phrase']),
                    'department': str(row['department'])
                })
            
            # Train the department detection model with uploaded data
            training_result = department_detection_system.train_model(training_data)
            
            # Clean up temp file
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            if "error" in training_result:
                return jsonify({"error": training_result["error"]}), 400
            
            return jsonify({
                "success": True,
                "message": "CSV uploaded and model trained successfully!",
                "training_metrics": training_result,
                "uploaded_records": len(training_data),
                "file_columns": list(df.columns)
            })
            
        except Exception as csv_error:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            return jsonify({"error": f"CSV processing failed: {str(csv_error)}"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# Department Detection API Routes
@app.route('/api/department-detect/predict', methods=['POST'])
@login_required
def predict_department():
    """Predict department based on request description"""
    try:
        data = request.get_json()
        phrase = data.get('phrase', '').strip()
        
        if not phrase:
            return jsonify({"error": "Request description is required"}), 400
        
        # Make prediction
        prediction = department_detection_system.predict_department(phrase)
        
        if "error" in prediction:
            return jsonify({"error": prediction["error"]}), 400
        
        return jsonify({
            "success": True,
            "prediction": prediction
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/api/department-detect/model-status', methods=['GET'])
@login_required
def get_department_detection_status():
    """Get the current status of the department detection model"""
    try:
        model_info = department_detection_system.get_model_info()
        
        return jsonify({
            "success": True,
            "model_info": model_info
        })
        
    except Exception as e:
        return jsonify({"error": f"Status check failed: {str(e)}"}), 500

@app.route('/api/department-detect/test-samples', methods=['GET'])
@login_required
def test_department_detection_samples():
    """Test the model with sample phrases"""
    try:
        if current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        
        test_results = department_detection_system.test_sample_phrases()
        
        if "error" in test_results:
            return jsonify({"error": test_results["error"]}), 400
        
        return jsonify({
            "success": True,
            "test_results": test_results
        })
        
    except Exception as e:
        return jsonify({"error": f"Test failed: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🔧 Database tables created/updated")
        # Do not print secrets in logs for public repositories
        print(f"🔧 Flask app name: {app.name}")
    app.run(debug=True)
