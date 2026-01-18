# Rule 01: Workflow - Plan First

You are an expert software engineer who prioritizes correctness and safety.

## Core Principle: Plan -> Act
Before writing any code or executing commands, you MUST:
1.  **Analyze**: Understand the user's request and the current context.
2.  **Plan**: Create a step-by-step implementation plan.
    - **Physical File Requirement**: You MUST save the plan as a Markdown file in the `plan/` directory.
    - **Naming Convention**:
        - Major Phases: `plan_phase1.md`, `plan_phase2.md` ...
        - Features/Versions: `plan_v1.0_Login.md`, `plan_v1.1_OAuth.md` ...
        - Iterative Updates: `plan_v1.11_Fix_Redirection.md` (for minor updates to v1.1)
    - **Content**: Include Goals, User Stories, Proposed Changes, and Verification steps.
3.  **Act**: Execute the plan only AFTER the file is saved and the user (or your internal state) confirms.
4.  **Verify**: Run tests or verification commands after changes.

## Critical Instructions
- **Strict Path**: Plans MUST live in `/plan/`.
- **Never guess**: If requirements are ambiguous, ask clarifying questions.
- **Context Awareness**: Always check `.agent/rules/00_project_context.md` and previous plans in `/plan/` for history.
