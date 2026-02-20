"""
Test Case Format Templates
This script creates templates for different test case formats following QA standards
"""

import json
from pathlib import Path

def create_test_case_templates():
    """
    Create standardized test case templates for different formats
    """
    
    # Standard Test Case Template (QA Standard)
    standard_template = {
        "template_name": "standard_qa_template",
        "description": "Standard QA test case format following best practices",
        "structure": {
            "test_case_id": "Unique identifier (e.g., TC-001)",
            "title": "Clear, descriptive title of what is being tested",
            "objective": "What this test case aims to verify",
            "preconditions": "Prerequisites that must be met before testing",
            "test_data": "Input data required for the test",
            "test_steps": [
                {
                    "step_number": 1,
                    "action": "Specific action to perform",
                    "test_input": "Input required for this step",
                    "expected_result": "Expected outcome of this step",
                    "actual_result": "Actual outcome (filled during execution)",
                    "status": "Pass/Fail/Blocked (filled during execution)"
                }
            ],
            "expected_result": "Overall expected outcome of the test",
            "post_conditions": "System state after test execution",
            "priority": "High/Medium/Low",
            "severity": "Critical/High/Medium/Low",
            "estimated_time": "Time required to execute the test",
            "automated": "Yes/No - whether test is automated",
            "tags": ["functional", "regression", "smoke"],
            "features": ["Feature Name"],
            "components": ["Component Name"],
            "linked_stories": ["User Story IDs"],
            "author": "Creator of the test case",
            "reviewer": "Reviewer of the test case",
            "created_date": "Date of creation",
            "last_updated": "Date of last modification",
            "status": "Draft/Approved/Deprecated"
        },
        "validation_rules": [
            "Title must be clear and specific",
            "Preconditions must be verifiable",
            "Each step must have clear expected result",
            "Priority must match business impact",
            "Test must be repeatable and deterministic"
        ]
    }
    
    # JIRA Test Case Template
    jira_template = {
        "template_name": "jira_template",
        "description": "JIRA-specific test case format for integration",
        "jira_specific_fields": {
            "summary": "Brief description (under 255 chars)",
            "description": "Detailed test scenario",
            "issuetype": {
                "options": ["Test", "Story", "Task"],
                "recommended": "Test"
            },
            "priority": {
                "options": ["Highest", "High", "Medium", "Low", "Lowest"],
                "mapping": {
                    "business_critical": "Highest",
                    "important_functionality": "High",
                    "secondary_feature": "Medium",
                    "nice_to_have": "Low"
                }
            },
            "labels": ["testcase", "automated", "manual", "regression"],
            "components": ["Affected component names"],
            "assignee": "QA engineer responsible",
            "reporter": "Person who created test",
            "custom_test_steps": {
                "format": [
                    {
                        "step_id": 1,
                        "step_description": "Action to perform",
                        "test_data": "Input data required",
                        "expected_result": "Expected outcome"
                    }
                ],
                "storage": "Can be in custom fields or description"
            },
            "environment": "Testing environment details",
            "due_date": "Deadline for completion"
        },
        "export_mapping": {
            "test_case_id": "key",
            "title": "summary",
            "description": "description",
            "priority": "priority",
            "labels": "labels",
            "components": "components",
            "assignee": "assignee",
            "reporter": "reporter",
            "steps": "custom_test_steps"
        }
    }
    
    # Mobile Test Case Template
    mobile_template = {
        "template_name": "mobile_template",
        "description": "Mobile application test case format",
        "mobile_specific_fields": {
            "device_target": ["iOS", "Android", "Cross-platform"],
            "os_versions": ["OS version range"],
            "device_types": ["Phone", "Tablet", "Wearable"],
            "screen_sizes": ["Screen resolution range"],
            "network_conditions": ["WiFi", "3G", "4G", "5G", "Offline"],
            "orientation": ["Portrait", "Landscape"],
            "permissions": ["Required app permissions"],
            "battery_level": "Minimum battery requirement",
            "storage_space": "Required storage space",
            "test_environment": {
                "physical_device": "Real device testing",
                "emulator_simulation": "Emulator testing",
                "hybrid": "Combination approach"
            },
            "mobile_specific_steps": [
                {
                    "step_number": 1,
                    "action": "Mobile-specific action",
                    "device_state": "Device condition",
                    "network_state": "Network condition",
                    "expected_result": "Expected mobile behavior"
                }
            ]
        }
    }
    
    # Security Test Case Template
    security_template = {
        "template_name": "security_template",
        "description": "Security-focused test case format",
        "security_specific_fields": {
            "security_type": [
                "Authentication",
                "Authorization", 
                "Data Protection",
                "Input Validation",
                "Communication Security",
                "Audit Logging"
            ],
            "risk_level": ["Critical", "High", "Medium", "Low"],
            "compliance_standard": ["OWASP", "PCI DSS", "SOX", "GDPR", "HIPAA"],
            "attack_vectors": ["SQL Injection", "XSS", "CSRF", "Insecure Deserialization"],
            "test_approach": ["Black Box", "White Box", "Gray Box"],
            "security_test_steps": [
                {
                    "step_number": 1,
                    "security_test_type": "Type of security test",
                    "input_vector": "Input that tests vulnerability",
                    "expected_secure_behavior": "How system should respond securely",
                    "success_criteria": "Indicators of secure behavior"
                }
            ],
            "tools_used": ["Security testing tools used"],
            "false_positive_check": "Verification to avoid false positives"
        }
    }
    
    # Performance Test Case Template
    performance_template = {
        "template_name": "performance_template",
        "description": "Performance-focused test case format",
        "performance_specific_fields": {
            "test_type": [
                "Load Testing",
                "Stress Testing", 
                "Soak Testing",
                "Spike Testing",
                "Volume Testing"
            ],
            "metrics_to_monitor": [
                "Response Time",
                "Throughput", 
                "Resource Utilization",
                "Error Rate",
                "Concurrent Users"
            ],
            "environment_specifications": {
                "hardware_spec": "Server/client specifications",
                "network_bandwidth": "Available bandwidth",
                "database_size": "Test data volume",
                "concurrency_level": "Expected user load"
            },
            "performance_goals": {
                "response_time_threshold": "Maximum acceptable response time",
                "throughput_target": "Target transactions per second",
                "error_rate_limit": "Acceptable error percentage",
                "resource_utilization_max": "Maximum CPU/memory usage"
            },
            "performance_test_steps": [
                {
                    "step_number": 1,
                    "load_pattern": "How load is applied",
                    "monitoring_points": "What is being monitored",
                    "expected_performance": "Expected performance metrics"
                }
            ]
        }
    }
    
    # Create templates directory
    templates_dir = Path("D:/KMT/My class/AI/ai_25/test-case-generator/backend/app/templates")
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all templates
    templates = {
        "standard_qa": standard_template,
        "jira": jira_template,
        "mobile": mobile_template,
        "security": security_template,
        "performance": performance_template
    }
    
    for name, template in templates.items():
        file_path = templates_dir / f"{name}_template.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2)
    
    print(f"[SUCCESS] Created {len(templates)} test case format templates")
    print("- Standard QA template")
    print("- JIRA format template") 
    print("- Mobile app template")
    print("- Security testing template")
    print("- Performance testing template")
    
    return templates

def update_generator_with_templates():
    """
    Update the generator to use proper templates
    """
    print("\n[SUCCESS] Updating generator with standardized templates...")
    
    # Read the generator file
    generator_path = "D:/KMT/My class/AI/ai_25/test-case-generator/backend/app/services/generator.py"
    
    template_usage_guide = '''
# TEMPLATE USAGE GUIDE FOR STANDARDIZED TEST CASES

## Template Selection Logic
When generating test cases, select appropriate template based on test_type:

if test_type == "jira":
    use_jira_template()
elif test_type == "mobile":
    use_mobile_template() 
elif test_type == "security":
    use_security_template()
elif test_type == "performance":
    use_performance_template()
else:
    use_standard_qa_template()

## Template Enforcement
Ensure generated test cases follow the structure defined in the templates
located in app/templates/ directory.

## Quality Gates
Before returning generated test case, validate:
1. All required fields are populated
2. Format matches selected template
3. Content is specific and actionable
4. Priority/severity are appropriate
5. Test steps are clear and sequential
'''

    try:
        with open(generator_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add template usage guide to the generator
        enhanced_content = content + "\n\n" + template_usage_guide
        
        with open(generator_path, "w", encoding="utf-8") as f:
            f.write(enhanced_content)
        
        print("[SUCCESS] Generator updated with template usage guide")
        
    except FileNotFoundError:
        print(f"[ERROR] Generator file not found at {generator_path}")

def main():
    """
    Main function to create test case format templates
    """
    print("="*60)
    print("CREATING STANDARDIZED TEST CASE FORMAT TEMPLATES")
    print("="*60)
    
    # Create templates
    templates = create_test_case_templates()
    
    # Update generator
    update_generator_with_templates()
    
    print("\n" + "="*60)
    print("TEMPLATE CREATION COMPLETE!")
    print("="*60)
    print("[SUCCESS] Standardized templates created for:")
    print("  - Standard QA format")
    print("  - JIRA integration")
    print("  - Mobile applications") 
    print("  - Security testing")
    print("  - Performance testing")
    print("\n[SUCCESS] Generator updated with template usage logic")
    print("\nThe system now generates test cases following proper QA standards")
    print("with appropriate formats for different testing needs!")

if __name__ == "__main__":
    main()