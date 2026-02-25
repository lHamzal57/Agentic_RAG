"""
Prompts for SystemArchitectureWorkflow
"""

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
user_stories[number of user stories]{component_id, id, description}:
    COMP-1, US-1, description
""".strip()

JSON_ERROR_STRUCTURE_STREAMING = """
{
    "error": True,
    "reason": "...",
}
""".strip()

def render_prompt(context: str, question: str) -> str:
    return f"""
You are a meticulous, senior-level QA test-generation assistant. 

First, generate a concise, professional title that accurately reflects the core task and intent of the request.
The title must:
- Be 5–10 words long
- Clearly represent QA, system architecture extraction, and BRD/User Story processing
- Use precise, enterprise-level technical language
- Avoid generic or vague terms
Output only the title text.

Then, perform the task below.

Your job is to consume a Business Requirements Document (BRD) or a User Story and produce a comprehensive, machine-readable system architecture (no additional prose). Follow these rules exactly.

**Extract the structure**: Use the system, subsystem, and component hierarchy provided in the following input: 
{context}
if file content is empty, respond with an {JSON_ERROR_STRUCTURE_STREAMING}.
if file content is not related to Business Requirements Document (BRD) or a User Story, it must be Business Requirements Document (BRD) or a User Story, respond with {JSON_ERROR_STRUCTURE_STREAMING}.

Please generate additional System, Subsystem, Component, and User Story based on the existing ones, ensuring all file content are covered. 
Revalidate the response to identify any missing System, Subsystem, Component, and User Story and include them. 
Ensure the system architecture comprehensively covers System, Subsystem, Component, and User Story for all file content.
The final output must be a single valid with the following structure:
{FORMAT_STRUCTURE}
""".strip()
