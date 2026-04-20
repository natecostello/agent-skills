---
name: submit-monthly-expenses
description: >-
  Monthly expense management workflow for AMPS Unlimited 1.0 LLC. Handles
  downloading receipts from vendor portals (Google Workspace, AWS, WyomingAgents,
  Zenbusiness Banking, GitHub, Anthropic), renaming files to standard format,
  organizing in the expense receipts folder, uploading to Zoho Expense, and
  generating monthly expense reports. Use when processing monthly business
  expenses, reconciling receipts, or preparing expense reports.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

# Monthly Expenses Workflow

Process monthly LLC expenses step-by-step: download → rename → organize → upload → report.

## Receipt Folder

**Location:** `/Users/ncos/Documents/File_cabinet/AMPS Unlimited/Expense Reciepts`

## File Naming Convention

Format: `YYYY-MM-DD-Vendor.pdf`

Examples:
- `2026-01-01-Google Workspace.pdf`
- `2026-01-01-AWS.pdf`
- `2026-01-07-WyomingAgents - Virtual Office.pdf`
- `2026-01-15-GitHub.pdf`
- `2026-01-18-zb-banking-3686821.pdf` (preserves invoice number)
- `2026-01-26-Anthropic-Receipt-2823-4502-6365.pdf` (preserves receipt number)

## Monthly Workflow

### Step 0: Setup

1. **Create monthly folder:** Create `Downloads/YYYY-Mon-Expenses/` (e.g., `2026-Feb-Expenses`)

2. **Open browser tabs** to all login pages:
   - AWS: https://console.aws.amazon.com/billing
   - GitHub: https://github.com/settings/billing
   - Anthropic: https://claude.ai/settings/billing
   - WyomingAgents: https://accounts.wyomingagents.com
   - Zenbusiness: https://www.zenbusiness.com/my-business
   - Google Workspace: https://admin.google.com/ac/billing (requires AMPS Unlimited Chrome profile)
   - Zoho Expense: https://expense.zoho.com
   - YNAB: https://app.ynab.com

3. **Prompt user:** "Please log into all vendor sites, Zoho Expense, and YNAB. Also add any ad-hoc/manual receipts to `Downloads/YYYY-Mon-Expenses/`. Let me know when ready."

4. **Wait for user confirmation** before proceeding to Step 1.

### Step 1: Download Receipts

Once user confirms login, assist with navigating to and downloading receipts from each portal.

**Regular monthly vendors (see references/vendors.md for details):**

| Vendor | Billing Date | Portal |
|--------|--------------|--------|
| Google Workspace | ~1st | admin.google.com → Billing (AMPS Unlimited Chrome profile) |
| AWS | ~1st | console.aws.amazon.com → Billing |
| WyomingAgents Virtual Office | ~7th | accounts.wyomingagents.com → Account |
| GitHub | ~15th | github.com/settings/billing |
| Zenbusiness Banking | ~18th | zenbusiness.com → My Business → Order History |
| Anthropic | ~26th | claude.ai/settings/billing |

**Periodic vendors:** Biberk insurance, Squarespace domains, Zoho, Toggl, ChatGPT

For each download, confirm with user before saving.

### Step 2: Rename and Organize Files

After each download, rename and move to the monthly working folder:

1. Identify downloaded file (usually in Downloads root)
2. Determine correct date (**paid date** from receipt, not invoice/billing period date)
3. Rename to: `YYYY-MM-DD-Vendor.pdf` (preserve invoice numbers when present in downloaded filename)
4. Move to `Downloads/YYYY-Mon-Expenses/` folder created in Step 0

**Note:** After workflow complete, user migrates folder contents to archive: `/Users/ncos/Documents/File_cabinet/AMPS Unlimited/Expense Reciepts`

### Step 2b: Verify Against YNAB

Once all receipts are gathered, verify the total against YNAB:

1. Navigate to YNAB (user already logged in from Step 0)
2. Find the **"Nate Business/Expenses Reimbursable"** category
3. Check the category activity (shows as negative outflow)
4. Compare to the total of gathered receipts
5. **If totals don't match:** STOP and notify user of discrepancy - do not proceed until resolved
6. **If totals match:** Continue to Step 3

### Step 3: Upload to Zoho Expense

1. Claude navigates to Zoho Expense (user already logged in from Step 0)
2. Claude prompts user: "Please select all files from `Downloads/YYYY-Mon-Expenses/` using the 'Drag Receipts' area or file picker"
3. User performs one file selection (drag-drop or picker) - **this is the only manual step during upload**
4. Zoho auto-extracts data from receipts
5. Claude verifies each expense entry:
   - Confirm date matches receipt
   - Confirm amount matches receipt
   - Set correct category (reference vendors.md for mappings)
   - Save entry

**Note:** Zoho allows max 5 files per upload. For months with 6+ receipts, two uploads are needed.

### Step 4: Generate and Submit Expense Report

1. Navigate to Reports in Zoho Expense
2. Create new expense report:
   - **Name:** `YYYY Month Expenses` (e.g., "2026 January Expenses")
   - **Duration:** 1st to last day of month (e.g., 01 Jan 2026 - 31 Jan 2026)
3. Click "Add Unreported Expenses" and select all expenses for the month
4. Verify report total matches YNAB balance (already confirmed in Step 2b)
5. **Submit the report** (YNAB verification passed, so auto-submit is authorized)
6. Notify user: report submitted, remind to migrate receipt folder to archive

## Browser Automation Notes

**Login workflow:** Navigate to vendor login page, user logs in manually, then Claude assists with navigation and downloads.

**Chrome profile requirements:**
- Google Workspace requires AMPS Unlimited Chrome profile
- Other vendors work with personal Chrome profile

**PDF download technique:** When PDFs open in browser viewer and toolbar clicks don't register, use JavaScript:
```javascript
const a = document.createElement('a'); a.href = window.location.href; a.download = 'filename.pdf'; a.click();
```

**When using Claude in Chrome for Zoho Expense:**
- User must be logged into Zoho before automation
- Verify each expense entry before saving
- Take screenshots to confirm successful uploads
- Check for duplicate entries before creating new ones
