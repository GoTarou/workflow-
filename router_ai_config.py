import os
from typing import Optional, Dict, Any
import requests
import json

class RouterAIConfig:
    def __init__(self):
        # Read from environment in public repositories; avoid hardcoding secrets
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.mock_mode = False  # Now using real Gemini AI API
        
        # Company Automation Assistant Prompt
        self.company_assistant_prompt = """You are a company automation assistant.  
Your job is to read employee messages and route them to the correct department.  

Step 1: Identify the department based on message content. Possible departments:  
- HR (leave requests, salary, payroll, benefits, vacation)  
- Sales (customer orders, leads, deals, invoices)  
- Facilities (building issues, repairs, maintenance, office supplies)  
- IT (technical issues, login problems, software requests, hardware issues)  
- Other (if none of the above clearly fit)

Step 2: Determine priority level based on urgency indicators:
- Urgent: "emergency", "broken", "down", "urgent", "asap", "immediately", "critical", "not working"
- High: "important", "blocking", "urgent", "priority", "need help now"
- Normal: "request", "would like", "need", "want to", "planning"
- Low: "when possible", "no rush", "sometime", "future"

Step 3: Extract important information:
- employee name (if mentioned)
- relevant dates (if any)
- reason or description of the request
- original message

Step 4: Return the result in structured JSON:
{
   "department": "HR | Sales | Facilities | IT | Other",
   "priority": "urgent | high | normal | low",
   "employee": "Name if given, else null",
   "dates": "Any dates mentioned, else null",
   "details": "Reason/description in plain text",
   "raw_message": "Original message"
}"""

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _mock_analysis_response(self, document_path: str, analysis_type: str) -> Dict[str, Any]:
        """Generate mock analysis response based on document content"""
        filename = os.path.basename(document_path)
        
        # Simulate different analysis types
        if analysis_type == "hr":
            return {
                "document_info": {
                    "filename": filename,
                    "analysis_type": "HR Analysis"
                },
                "summary": "This document contains HR-related information including employee policies, benefits, and leave requests.",
                "classification": {
                    "category": "HR",
                    "confidence": 0.95,
                    "subcategories": ["Employee Benefits", "Leave Management", "Policy Documents"]
                },
                "key_points": [
                    "Employee leave policy updates",
                    "Benefits enrollment procedures",
                    "Performance review guidelines"
                ],
                "priority": "High",
                "action_required": "Review and approve policy changes"
            }
        elif analysis_type == "sales":
            return {
                "document_info": {
                    "filename": filename,
                    "analysis_type": "Sales Analysis"
                },
                "summary": "Sales document containing customer information, deals, and revenue projections.",
                "classification": {
                    "category": "Sales",
                    "confidence": 0.92,
                    "subcategories": ["Customer Management", "Deal Pipeline", "Revenue Analysis"]
                },
                "key_points": [
                    "Q4 sales targets and achievements",
                    "New customer acquisitions",
                    "Revenue projections for next quarter"
                ],
                "priority": "Medium",
                "action_required": "Update sales forecast"
            }
        else:
            return {
                "document_info": {
                    "filename": filename,
                    "analysis_type": "General Analysis"
                },
                "summary": "General document analysis completed successfully with comprehensive insights.",
                "classification": {
                    "category": "General",
                    "confidence": 0.88,
                    "subcategories": ["Document Review", "Content Analysis", "Information Extraction"]
                },
                "key_points": [
                    "Document structure identified",
                    "Key content extracted",
                    "Summary generated"
                ],
                "priority": "Normal",
                "action_required": "Review analysis results"
            }

    def _mock_text_extraction(self, document_path: str) -> Dict[str, Any]:
        """Generate mock text extraction response"""
        filename = os.path.basename(document_path)
        return {
            "document": filename,
            "text_length": 1250,
            "formatting_preserved": True,
            "tables_extracted": 2,
            "extracted_text": "This is a sample extracted text from the document. It contains important information that has been processed and formatted for easy reading. The text includes various sections with different formatting styles and may contain tables or structured data.",
            "metadata": {
                "pages": 3,
                "language": "English",
                "confidence": 0.94
            }
        }

    def _mock_classification(self, document_path: str) -> Dict[str, Any]:
        """Generate mock document classification response"""
        filename = os.path.basename(document_path)
        return {
            "document": filename,
            "classification": {
                "primary_category": "Business Document",
                "confidence": 0.89,
                "subcategories": ["Report", "Analysis", "Policy"],
                "tags": ["business", "analysis", "documentation"],
                "suggested_workflow": "Review → Approve → Archive"
            }
        }

    def _mock_summarization(self, document_path: str, summary_length: str = "medium") -> Dict[str, Any]:
        """Generate mock document summarization response"""
        filename = os.path.basename(document_path)
        
        summaries = {
            "short": "Document contains business analysis and recommendations for Q4 planning.",
            "medium": "This document provides a comprehensive analysis of business performance, including key metrics, challenges, and strategic recommendations for the upcoming quarter. It covers financial data, operational insights, and actionable next steps.",
            "long": "This comprehensive business document presents a detailed analysis of organizational performance across multiple dimensions. It includes financial metrics, operational data, market analysis, and strategic insights. The document identifies key challenges, opportunities, and provides detailed recommendations for improvement. It also contains supporting data, charts, and appendices with additional context."
        }
        
        return {
            "document": filename,
            "summary_length": summary_length,
            "summary": summaries.get(summary_length, summaries["medium"]),
            "key_points": [
                "Business performance analysis completed",
                "Key challenges identified",
                "Strategic recommendations provided",
                "Action items outlined"
            ]
        }

    def _mock_message_routing(self, message: str) -> Dict[str, Any]:
        """Generate mock message routing response using the company assistant prompt"""
        # Simulate intelligent routing based on message content
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["leave", "vacation", "salary", "payroll", "benefits", "hr", "off", "time off", "holiday", "honeymoon", "married", "wedding"]):
            department = "HR"
            details = "Employee request related to HR matters"
        elif any(word in message_lower for word in ["customer", "order", "lead", "deal", "invoice", "sales"]):
            department = "Sales"
            details = "Sales-related inquiry or request"
        elif any(word in message_lower for word in ["building", "repair", "maintenance", "office supplies", "facility"]):
            department = "Facilities"
            details = "Facility or building maintenance request"
        elif any(word in message_lower for word in ["technical", "login", "software", "hardware", "computer", "system"]):
            department = "IT"
            details = "Technical support or IT-related request"
        else:
            department = "Other"
            details = "General inquiry or request"
        
        # Determine priority based on urgency indicators
        if any(word in message_lower for word in ["emergency", "broken", "down", "urgent", "asap", "immediately", "critical", "not working"]):
            priority = "urgent"
        elif any(word in message_lower for word in ["important", "blocking", "priority", "need help now"]):
            priority = "high"
        elif any(word in message_lower for word in ["when possible", "no rush", "sometime", "future"]):
            priority = "low"
        else:
            priority = "normal"
        
        # Extract employee name (simplified mock)
        employee = None
        if "john" in message_lower or "jane" in message_lower or "employee" in message_lower:
            employee = "Employee Name"
        
        # Extract dates (simplified mock)
        dates = None
        if any(word in message_lower for word in ["tomorrow", "next week", "monday", "friday"]):
            dates = "Upcoming date mentioned"
        
        return {
            "department": department,
            "priority": priority,
            "employee": employee,
            "dates": dates,
            "details": details,
            "raw_message": message
        }

    def analyze_document(self, document_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze document using Router AI"""
        if self.mock_mode:
            return self._mock_analysis_response(document_path, analysis_type)
        
        # Real API implementation would go here
        try:
            # Read document content
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prepare API request with the company assistant prompt
            payload = {
                "document": content,
                "analysis_type": analysis_type,
                "prompt": self.company_assistant_prompt,
                "format": "json"
            }
            
            response = requests.post(
                f"{self.base_url}/analyze",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def extract_text(self, document_path: str) -> Dict[str, Any]:
        """Extract text from document using Router AI"""
        if self.mock_mode:
            return self._mock_text_extraction(document_path)
        
        # Real API implementation would go here
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "document": content,
                "prompt": self.company_assistant_prompt,
                "extraction_type": "text"
            }
            
            response = requests.post(
                f"{self.base_url}/extract",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Text extraction failed: {str(e)}"}

    def summarize_document(self, document_path: str, summary_length: str = "medium") -> Dict[str, Any]:
        """Summarize document using Router AI"""
        if self.mock_mode:
            return self._mock_summarization(document_path, summary_length)
        
        # Real API implementation would go here
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "document": content,
                "summary_length": summary_length,
                "prompt": self.company_assistant_prompt,
                "format": "structured"
            }
            
            response = requests.post(
                f"{self.base_url}/summarize",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Summarization failed: {str(e)}"}

    def classify_document(self, document_path: str) -> Dict[str, Any]:
        """Classify document using Router AI"""
        if self.mock_mode:
            return self._mock_classification(document_path)
        
        # Real API implementation would go here
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            payload = {
                "document": content,
                "prompt": self.company_assistant_prompt,
                "classification_type": "department_routing"
            }
            
            response = requests.post(
                f"{self.base_url}/classify",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Classification failed: {str(e)}"}

    def route_message(self, message: str) -> Dict[str, Any]:
        """Route employee message to correct department using Google Gemini AI"""
        if self.mock_mode:
            return self._mock_message_routing(message)
        
        # Real Google Gemini AI API implementation
        try:
            # Format the prompt for Gemini
            system_prompt = self.company_assistant_prompt
            user_message = f"Please analyze this employee message and route it to the correct department: {message}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\n{user_message}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,  # Low temperature for consistent routing
                    "maxOutputTokens": 500,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            response = requests.post(
                f"{self.base_url}/gemini-1.5-flash:generateContent?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                
                # Try to parse JSON response from AI
                try:
                    # Extract JSON from the response (AI might wrap it in markdown)
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        parsed_response = json.loads(json_str)
                        return parsed_response
                    else:
                        # Fallback: try to parse the entire response
                        return json.loads(ai_response)
                        
                except json.JSONDecodeError:
                    # If JSON parsing fails, fall back to mock routing
                    print(f"AI response parsing failed, using mock routing. Response: {ai_response}")
                    return self._mock_message_routing(message)
                    
            else:
                return {"error": f"Gemini AI API request failed: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"Message routing failed: {str(e)}"}

# Create a global instance
router_ai = RouterAIConfig()
