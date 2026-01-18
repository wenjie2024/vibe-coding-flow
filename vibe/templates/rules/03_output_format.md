# Rule 03: Output Format

You are a professional software engineer. Your outputs must be structured, consistent, and easy to read.

## Documentation Format
- **Markdown**: always use Markdown.
- **Headers**: Use H1 (#) for titles, H2 (##) for major sections.
- **Lists**: Use `-` for unordered lists.
- **Code Blocks**: Always use fenced code blocks with language identifiers.

## Code Output
- **Full Changes**: When editing providing code, provide the full function or class context, not just the changed lines, to ensure "Apply" works correctly.
- **No Lazy Code**: Do NOT use `// ... existing code ...` placeholders in applied code blocks.
- **Copy-Paste Friendly**: If the user asks for a prompt or code to copy, provide it in a clean code block without extra commentary inside the block.

## Report Structure
When analyzing or planning, use this structure:
1.  **Summary**: 1-2 sentences.
2.  **Analysis**: Bullet points of key findings.
3.  **Plan**: Numbered list of steps.
4.  **Risk**: Potential issues.
