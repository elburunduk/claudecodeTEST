# Workflow: [Name]

## Objective
One sentence. What does this workflow produce or achieve?

## Inputs
| Input | Source | Notes |
|-------|--------|-------|
| `example_input` | Provided by user / another tool | Required |

## Steps

### 1. [Step name]
- **Tool:** `tools/example_tool.py`
- **Command:** `python tools/example_tool.py --arg value`
- **Output:** What the script produces (file path, printed result, etc.)

### 2. [Step name]
- **Tool:** `tools/another_tool.py`
- **Command:** `python tools/another_tool.py --input .tmp/previous_output.json`
- **Output:** ...

## Expected Output
Describe what success looks like. Where does the final result go (Google Sheet, printed JSON, file)?

## Edge Cases & Known Issues
- **Rate limits:** e.g., API X allows 100 req/min — tool handles this with exponential backoff
- **Auth errors:** Run `python tools/google_auth.py` to refresh token
- **Empty results:** If step 2 returns 0 rows, check input format matches expected schema

## Learned Improvements
<!-- Updated as the workflow evolves. Newest entries at the top. -->
- [Date] — [What changed and why]
