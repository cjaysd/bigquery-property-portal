# Claude Agent Instructions - Google BigQuery Project

## Global Resources Available
This project has access to company-wide resources via symbolic links:

### Implementation Guides: `./global-guides/`
- List guides: `ls ./global-guides/`
- Search guides: `grep -r "pattern" ./global-guides/`
- Read guide: `cat ./global-guides/[guide-name].md`

### Sub-Agents: `./claude-agents/`
- List agents: `ls ./claude-agents/`
- Search agents: `grep -r "description" ./claude-agents/`
- Read agent spec: `cat ./claude-agents/[agent-name].md`

### Slash Commands: `./claude-commands/`
- List commands: `ls ./claude-commands/`
- Search commands: `grep -r "description" ./claude-commands/`
- Read command help: `cat ./claude-commands/[command-name].md`

### CLAUDE Rule Hierarchy: `./CLAUDE-*.md`
- List rules: `ls ./CLAUDE-*.md`
- Read workspace rules: `cat ./CLAUDE-workspace.md`
- Read user rules: `cat ./CLAUDE-user.md`

### Priority Guides for This Project (Data/API Integration):
1. **Application Architecture Patterns** - Standard project structures and patterns
2. **AI-Assisted Development Workflow Guide** - Best practices for AI development
3. **API Integration Patterns** - External service integration best practices

### Before implementing:
1. Check for existing patterns in guides
2. Browse available agents for task automation
3. Use established slash commands for common workflows
4. Review CLAUDE rule hierarchy for context-specific instructions
5. Follow company standards

### Resource Categories:
- **Guides**: API Integration, Architecture, AI Development, UI Components, Workflows
- **Agents**: Specialized automation for debugging, testing, documentation, architecture
- **Commands**: Project setup, analysis, enhancement, debugging workflows
- **CLAUDE Rules**: Workspace-level and User-level instructions

### Project-Specific Context:
This is a Google BigQuery analytics project with:
- Python Flask backend (app.py)
- HTML templates for dashboards and analysis
- PDF generation capabilities (Playwright)
- BigQuery integration for data analytics

### Usage Examples:
```bash
# Find API and data patterns
grep -r "API\|data\|analytics" ./global-guides/

# Find relevant agents for testing/debugging
grep -r "test\|debug\|api" ./claude-agents/ | head -5

# Browse architecture patterns
cat "./global-guides/Application Architecture Patterns-20250805183521.md"

# Check workspace rules
cat ./CLAUDE-workspace.md

# Search for BigQuery or Google Cloud patterns
grep -ri "google\|bigquery\|cloud" ./global-guides/
```

## Task Management

### Next Steps Query Handler
When asked "what's next", "what should I work on", or similar:
1. Read `/TODO.md` in project root (if exists)
2. Return incomplete items by priority (🔴 → 🟡 → 🟢)
3. Include context about blockers or dependencies
4. Update task status after completion

### Sprint Management
CURRENT_SPRINT: [maintained by sprint-tracker]