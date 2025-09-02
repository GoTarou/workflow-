## Frontend API Usage Overview

This document summarizes what was built and exactly which backend APIs the frontend calls, grouped by page. It includes HTTP methods, paths, expected payloads, and where each call is used in the UI templates.

### What was built
- AI-assisted request submission with automatic department routing and priority detection
- Manual workflow designer (drag-and-drop) to build approval steps
- Approvals dashboard for approvers/admins with approve/reject actions
- Document preview with Router AI features: quick analysis, text extraction, summarization, and classification
- Department approver management (admin)
- Analytics dashboard with date range filtering

---

## Requests page (`templates/requests.html`)

- GET `/api/requests`
  - Purpose: Load current user's requests
  - Usage: `loadRequests()` on page load

- GET `/api/user-info`
  - Purpose: Determine role (e.g., admin) to toggle UI actions
  - Usage: Within `loadRequests()` after fetching requests

- POST `/api/ai/route-message`
  - Purpose: AI routes free-text message to department and priority
  - Body:
    ```json
    { "message": "string" }
    ```
  - Usage: `submitNewRequest()` to pre-analyze request before submit

- POST `/api/requests/create`
  - Purpose: Create AI-routed request
  - Body:
    ```json
    { "message": "string", "department": "HR|IT|...", "priority": "low|normal|high|urgent" }
    ```
  - Usage: `finalizeRequest()` after AI routing

- GET `/api/requests/<id>`
  - Purpose: View details for a request
  - Usage: `viewRequestDetails(requestId)`

- DELETE `/api/requests/<id>`
  - Purpose: Delete a request (admin)
  - Usage: `deleteRequest(requestId)` via modal confirmation

- POST `/api/requests/create-workflow`
  - Purpose: Create request using manual workflow steps
  - Body:
    ```json
    {
      "title": "string",
      "message": "string",
      "priority": "low|normal|high|urgent",
      "workflow_steps": [ { "department": "HR|IT|...", "stepNumber": 1 } ]
    }
    ```
  - Usage: `submitWorkflowRequest()` when manual workflow is selected

- POST `/api/ai/suggest-workflow`
  - Purpose: ML suggests workflow steps from description
  - Body:
    ```json
    { "message": "string" }
    ```
  - Usage: `suggestMLWorkflow()` to auto-populate workflow canvas

---

## Approvals page (`templates/approvals.html`)

- GET `/api/requests`
  - Purpose: Load approvable requests list
  - Usage: `loadApprovals()` on page load and filter changes

- GET `/api/user-info`
  - Purpose: Check if admin to render delete actions
  - Usage: Inside `loadApprovals()`

- GET `/api/requests/<id>`
  - Purpose: Load request details for review modal
  - Usage: `reviewRequest(requestId)`

- POST `/api/requests/<id>/approve`
  - Purpose: Approve or reject a request
  - Body (approve):
    ```json
    { "action": "approve", "comments": "string" }
    ```
  - Body (reject):
    ```json
    { "action": "reject", "comments": "reason string" }
    ```
  - Usage: `approveRequest()` and `rejectRequest()`

- DELETE `/api/requests/<id>`
  - Purpose: Delete request (admin)
  - Usage: `deleteRequest(requestId)`

---

## Document Preview page (`templates/preview_document.html`)

- POST `/api/ai/quick-analysis/<doc_id>`
  - Purpose: All-in-one AI analysis on document
  - Usage: `performQuickAnalysis()`

- POST `/api/ai/extract/<doc_id>`
  - Purpose: Extract text from the document
  - Usage: `extractTextWithAI()`

- POST `/api/ai/summarize/<doc_id>`
  - Purpose: Generate a summary
  - Body:
    ```json
    { "summary_length": "short|medium|long" }
    ```
  - Usage: `summarizeDocument()`

- POST `/api/ai/classify/<doc_id>`
  - Purpose: Classify the document type
  - Usage: `classifyDocument()`

- POST `/api/ai/route-message`
  - Purpose: Route arbitrary employee messages (contextual helper)
  - Body:
    ```json
    { "message": "string" }
    ```
  - Usage: `routeMessage()`

---

## Manage Approvers (Admin) (`templates/manage_approvers.html`)

- GET `/api/department-approvers`
  - Purpose: List department approvers
  - Usage: `loadApprovers()`

- GET `/api/users`
  - Purpose: Populate approver dropdown (role = approver)
  - Usage: `loadUsers()`

- POST `/api/department-approvers`
  - Purpose: Create a department approver mapping
  - Body:
    ```json
    { "department": "HR|IT|...", "approver_id": 123 }
    ```
  - Usage: `addApprover()`

- DELETE `/api/department-approvers/<id>`
  - Purpose: Remove a department approver mapping
  - Usage: `removeApprover(approverId)`

---

## Analytics dashboard (`templates/analytics.html`)

- GET `/api/analytics/dashboard?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`
  - Purpose: Load analytics KPIs and charts for date range
  - Usage: On filter action

---

## Admin Users (Admin) (`templates/admin_users.html`)

Note: This page also exercises ML endpoints in the backend.

- POST `/api/ml/predict`
  - Purpose: Predict outcomes based on features
  - Usage: Example widget in admin page

- GET `/api/ml/analyze-patterns`
  - Purpose: Get ML-derived patterns/insights

- POST `/api/ml/export-data`
  - Purpose: Export dataset used for ML

- GET `/api/department-detect/model-status`
  - Purpose: Check Department Detection model status

- GET `/api/department-detect/test-samples`
  - Purpose: Get sample predictions for department detection

- POST `/api/ml/upload-csv`
  - Purpose: Upload CSV for retraining or analysis

---

## Machine Learning usage

This project uses classical ML models and utilities to enhance routing, forecasting, insights, and suggestions:

- Model artifacts (saved): see `models/`
  - `approval_time_model.pkl`, `approval_time_scaler.pkl`: Linear Regression model to predict approval time
  - `success_rate_model.pkl`, `success_rate_scaler.pkl`: Linear Regression model to predict success rate
  - `department_detection_model.pkl`, `department_detection_vectorizer.pkl`: Text classification to detect department from free text
  - `department_encoder.pkl`, `priority_encoder.pkl`, `scaler.pkl`, `feature_names.json`: encoders/scalers and feature list

- Training data/examples
  - `static/sample_training_data.csv` and `sample_training_data.csv`
  - Features are aligned with `models/feature_names.json`

- ML workflow endpoints (consumed from admin tools and internal flows)
  - POST `/api/ml/train`: Trains/updates ML workflow progression models
  - POST `/api/ml/predict`: Predicts workflow metrics from provided features
  - POST `/api/ml/suggest-workflow`: Generates suggested multi-step workflows from a request description
  - GET `/api/ml/analyze-patterns`: Returns discovered patterns/insights
  - POST `/api/ml/export-data`: Exports current training/evaluation data
  - GET `/api/ml/model-status`: Returns training and model metadata

- Linear Regression endpoints (time/success forecasting)
  - POST `/api/linear-regression/train-approval-time`: Train approval time regressor
  - POST `/api/linear-regression/train-success-rate`: Train success rate regressor
  - POST `/api/linear-regression/predict-approval-time`: Predict approval time
  - POST `/api/linear-regression/predict-success-rate`: Predict success probability
  - GET `/api/linear-regression/feature-importance`: Feature weights/importance
  - POST `/api/linear-regression/generate-insights`: Human-readable insights from coefficients

- Department detection (text ML)
  - GET `/api/department-detect/model-status`: Model health/status
  - GET `/api/department-detect/test-samples`: Example classifications for sample texts

- Where ML appears in the UI
  - `templates/requests.html`
    - ML Suggestion button uses POST `/api/ai/suggest-workflow` to build a suggested approval path
  - `templates/admin_users.html`
    - Exercises `/api/ml/predict`, `/api/ml/analyze-patterns`, `/api/ml/export-data`
    - Checks `/api/department-detect/model-status` and `/api/department-detect/test-samples`
  - `templates/analytics.html`
    - Surfaces data returned by `/api/analytics/dashboard` (which incorporates ML-derived metrics)

Notes
- Models are loaded and served by the Flask backend (`app.py`), with scalers/encoders applied consistently on both train and predict paths.
- Endpoints return `{ "success": true, ... }` payloads and include numeric predictions, feature weights, and suggested steps where applicable.

## Response shape notes
- Most endpoints respond with `{ "success": true, ... }` or `{ "error": "message" }`.
- Request entities include fields like `id`, `title`, `message`, `department`, `priority`, `status`, `created_at`, and arrays like `approvals` and `workflow_steps`.

---

## Authentication/Access
- All API calls in the UI require an authenticated session; many routes are protected with login requirements in the backend (`@login_required`).

---

## File references
- Requests UI: `templates/requests.html`
- Approvals UI: `templates/approvals.html`
- Document preview + AI tools: `templates/preview_document.html`
- Manage approvers: `templates/manage_approvers.html`
- Analytics: `templates/analytics.html`
- Admin Users (ML utilities): `templates/admin_users.html`

---

## Security & Public Repo Notes
- Do not hardcode secrets. The app reads `FLASK_SECRET_KEY`, `GEMINI_API_KEY`, and DB settings from environment variables.
- Avoid committing real connection strings, passwords, personal emails, or API keys.
- Sensitive/runtime files are excluded via `.gitignore` (e.g., `.env`, `flask_session/`, `uploads/`, `node_modules/`).
- Provide a `.env` locally; for CI/CD, configure secrets at the platform level.


