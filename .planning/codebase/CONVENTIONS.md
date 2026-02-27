# Coding Conventions

**Researched:** 2026-02-27  
**Domain:** Cline CLI + Azure DevOps MCP Server  
**Confidence:** HIGH

## Code Style
- **Indentation**: Use 2 spaces for indentation.
- **Line Length**: Limit lines to 80 characters for better readability.
- **Semicolons**: Use semicolons at the end of statements.

## Naming Conventions
- **Variables**: Use camelCase for variable names (e.g., `userName`, `totalCount`).
- **Functions**: Use camelCase for function names (e.g., `calculateTotal`, `fetchData`).
- **Classes**: Use PascalCase for class names (e.g., `UserService`, `ProductController`).

## Testing Practices
- **Test Framework**: Use Jest for unit testing.
- **Test Structure**: Organize tests in a `__tests__` directory adjacent to the source files.
- **Coverage**: Aim for at least 80% test coverage for all modules.

## Documentation
- **Comments**: Use JSDoc style comments for functions and classes.
- **README**: Keep the `README.md` updated with setup instructions and usage examples.

**Installation:**
```bash
npm install --save-dev jest