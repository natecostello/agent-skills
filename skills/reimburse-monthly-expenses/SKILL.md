---
name: reimburse-monthly-expenses
description: >-
  Monthly expense reimbursement workflow for AMPS Unlimited 1.0 LLC. Handles
  setting up reimbursement in Zoho Books, initiating transfer in Zenbusiness
  Banking, and recording the transaction in YNAB. Use after submitting the
  monthly expense report in Zoho Expense.
license: MIT
metadata:
  author: natecostello
  version: "0.1"
---

# Monthly Expense Reimbursement Workflow

Process monthly LLC expense reimbursement: Zoho Books → Zenbusiness Transfer → YNAB Recording.

## Prerequisites

- Monthly expense report must be submitted and approved in Zoho Expense (use `submit-monthly-expenses` skill first)

## Step 0: Setup

1. **Open browser tabs** to all required sites:
   - Zoho Books: https://books.zoho.com
   - Zenbusiness: https://www.zenbusiness.com
   - YNAB: https://app.ynab.com

2. **Prompt user:** "Please log into Zoho Books, Zenbusiness, and YNAB if needed. Let me know when ready."

3. **Wait for user confirmation** before proceeding to Step 1.

## Step 1: Setup Reimbursement in Zoho Books

1. Navigate to **Banking** in sidebar
2. Navigate to **"Checking"** account
3. Click **"Add Transaction"** dropdown
4. Select **"Employee Reimbursement"**
5. For **Employee Name**, select **"Nate Costello"** from dropdown
6. Select the **current month's Expense Report** from the list
7. In the **Description** field, enter: **"[Year] [Month] expense reimbursement (claude entry)"** (e.g., "2026 January expense reimbursement (claude entry)")
8. **DO NOT click SAVE yet** (will be done in Step 3)
9. **Note the amount to be reimbursed** - this will be used to verify in subsequent steps

## Step 2: Setup Reimbursement in Zenbusiness

1. Navigate to Banking: **Finances > Banking** OR click **"See all"** next to the Banking widget on the dashboard
2. Click **"Move Money"**
3. Select **"Send Money"**
4. Select destination: **"USAA Federal Savings Bank"**
5. Input **Amount** (must match Zoho Books reimbursement amount)
6. For memo/description, enter: **"[Year] [Month] expense reimbursement (claude entry)"** (e.g., "2026 January expense reimbursement (claude entry)")
7. Click **"Review Transfer"**
8. **Verify amounts match across all three sources:**
   - Zoho Books Employee Reimbursement amount
   - YNAB "Nate Business/Expenses Reimbursable" category activity
   - Zenbusiness transfer amount
9. **If discrepancy:** STOP and flag to user - do not proceed until resolved
10. **If all match:** Click **"Authorize"** to initiate the transfer

## Step 3: Record in Zoho Books

1. Return to Zoho Books Employee Reimbursement form
2. Click **SAVE** to record the reimbursement

## Step 4: Record Transaction in YNAB

1. In YNAB, select **"USAA Nate CHK"** account in the sidebar
2. Click **"Add Transaction"**
3. Fill in transaction details:
   - **Payee:** Amps Unlimited
   - **Category:** Nate Business: Expenses Reimbursable
   - **Memo:** [Year] [Month] expenses (claude entry) (e.g., "2026 January expenses (claude entry)")
   - **Outflow:** (leave blank)
   - **Inflow:** Amount of the transfer
4. Save the transaction

## Completion

Notify user: "Reimbursement complete. Transfer of $[amount] initiated from Zenbusiness to USAA. Recorded in Zoho Books and YNAB."

## Browser Automation Notes

- All three sites require user login before automation
- Zoho Books and Zenbusiness may have 2FA - wait for user to complete
- YNAB transaction entry is manual input - verify category autocomplete matches exactly
