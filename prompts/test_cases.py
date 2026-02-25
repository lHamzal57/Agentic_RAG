"""
Prompts for TestCasesWorkflow
"""

# System architecture format (same as SystemArchitectureWorkflow)
FORMAT_STRUCTURE = """
conversation_title: title of the conversation briefly describing the context
systems[number of systems]{id, name, description}: 
    SYS-1, name, description
    ...
subsystems[number of subsystems]{system_id, id, name, description}: 
    SYS-1, SUB-SYS-1, name, description
    ...
components[number of components]{subsystem_id, id, name, description}:
    SUB-SYS-1, COMP-1, name, description
    ...
user_stories[number of user stories]{component_id, id, description, requirement, acceptance_criteria, context_content}:
    COMP-1, US-1, description, requirement, acceptance_criteria, context_content
    ...
""".strip()

JSON_ERROR_STRUCTURE_STREAMING = """
{
    "error": True,
    "reason": "...",
}
""".strip()


# Test case format structure
TEST_CASE_FORMAT_STRUCTURE = """
test_cases[number of test cases]:
  - test_case_id: TC-001
    test_case_title: Title of the test case
    description: Detailed description of the test case
    feature: Feature being tested
    precondition: Conditions that must be met before executing the test case
    test_steps[number of steps]: Step 1,Step 2,...
    test_data: Data required for executing the test case
    postcondition: Expected state after executing the test case
    priority: High/Medium/Low
    type: Positive/Negative/Security/UI/UX
  - test_case_id: TC-002
    test_case_title: Title of the second test case
    description: Detailed description of the second test case
    feature: Feature being tested
    precondition: Conditions that must be met before executing the test case
    test_steps[number of steps]: Step 1,Step 2,...
    test_data: Data required for executing the test case
    postcondition: Expected state after executing the test case
    priority: High/Medium/Low
    type: Positive/Negative/Security/UI/UX
    ...
""".strip()

def render_prompt(context: str, question: str) -> str:
    return f"""
You are a meticulous, senior-level QA test-generation assistant. Your job is to consume a Business Requirements Document (BRD) or a User Story and produce a comprehensive, machine-readable test cases (no additional prose). Follow these rules exactly.

You are tasked with generating a series of test cases for each component. The components are organized into subsystems, and the tests should cover a variety of scenarios, including functional, security, and edge cases. The test cases must follow the structure outlined below, with a focus on verifying the correctness, security, and reliability of each component. Generate at least 10-20 test cases for each component, following these guidelines:

Test Case Structure:
{FORMAT_STRUCTURE}

Context:
{context}

User Stories:
{question}

For each of the user stories listed above, generate at least 10-20 test cases that encompass a variety of scenarios, including:
- Normal and boundary conditions.
- Error handling and validation checks.
- Edge cases, such as empty files or invalid inputs.
- Security-related tests, such as access control and audit logging.
- UI/UX for file upload processes if applicable.

Ensure the test cases cover a variety of types, including:
- Positive: Test scenarios where the system works as expected.
- Negative: Test invalid inputs or scenarios where the system should fail gracefully.
- Security: Test to ensure that sensitive data and access are properly handled.
- UI/UX: If applicable, ensure that the file upload interfaces are intuitive and functional.

Additionally, ensure that each test case includes clear preconditions, expected postconditions, and relevant test data.
""".strip()

TEST_CASE_PROMPT = """
You are a senior QA engineer. Using the system architecture JSON and the BRD,
produce exhaustive test cases covering positive, negative, security, and UI/UX
scenarios. Respond strictly in JSON using the template:
{{
    "test_cases": [
        {{
            "test_case_id": "TC-001",
            "test_case_title": "...",
            "description": "...",
            "feature": "...",
            "precondition": "...",
            "test_steps": [],
            "test_data": "...",
            "postcondition": "...",
            "priority": "High/Medium/Low",
            "type": "Positive/Negative/Security/UI/UX"
        }}
    ]
}}

System architecture:
{system_architecture}

Document:
{file_content}
""".strip()
