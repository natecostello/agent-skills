# Vendor Reference

## File Naming Conventions

- **Date format:** Always use zero-padded dates: `YYYY-MM-DD` (e.g., `2026-01-07`, not `2026-1-7`)
- **Date used:** Use the **paid date** from the invoice/receipt
- **Invoice numbers:** When present in downloaded filename, preserve them in the renamed file

## Zoho Expense Categories

| Category | Code | Vendors |
|----------|------|---------|
| Bank Fees and Charges | C-II-10 | Zenbusiness Inc. |
| Insurance | C-II-15 | BiBerk |
| Legal and Professional Services | C-II-17 | Wyoming Registered Agent Services LLC |
| Office Expense | C-II-18 | Squarespace |
| Supplies | C-II-22 | Best Buy, Amazon (equipment) |
| Software Subscriptions | C-II-27a | Google, AWS, OpenAI/ChatGPT, Toggl, Zoho, GitHub, Anthropic |

## Monthly Recurring Expenses

### Google Workspace
- **Billing date:** ~1st of month
- **File name format:** `YYYY-MM-DD-Google Workspace.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)
- **Portal:** admin.google.com → Billing → View payment history
- **Receipt location:** Payment history → Download invoice
- **Note:** Requires AMPS Unlimited Chrome profile (separate from personal profile)

### AWS
- **Billing date:** ~1st of month (invoice date, for previous month's usage)
- **File name format:** `YYYY-MM-DD-AWS.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)
- **Portal:** console.aws.amazon.com → Billing and Cost Management → Transactions
- **Receipt location:** Click invoice link to open PDF in browser viewer
- **Download technique:** Use JavaScript in browser console (PDF viewer toolbar clicks don't register):
  ```javascript
  const a = document.createElement('a'); a.href = window.location.href; a.download = 'filename.pdf'; a.click();
  ```

### WyomingAgents - Virtual Office
- **Billing date:** ~7th of month (paid date)
- **File name format:** `YYYY-MM-DD-WyomingAgents - Virtual Office.pdf`
- **Zoho category:** Legal and Professional Services (C-II-17)
- **Portal:** accounts.wyomingagents.com → Menu → Account → Invoices
- **Receipt location:** Select invoice checkbox → Download button

### Zenbusiness Banking
- **Billing date:** ~18th of month
- **File name format:** `YYYY-MM-DD-zb-banking-[invoice#].pdf`
- **Zoho category:** Bank Fees and Charges (C-II-10)
- **Portal:** zenbusiness.com → Dashboard → My Business → Order History → Download Receipts
- **Note:** Preserve invoice number from original downloaded filename (e.g., `invoice_3686821.pdf` → `2026-01-18-zb-banking-3686821.pdf`)

## Annual/Periodic Expenses

### WyomingAgents - Registered Agent Service
- **Billing:** Annual (~June)
- **File name format:** `YYYY-MM-DD-WyomingAgents - Registered Agent Service.pdf`
- **Zoho category:** Legal and Professional Services (C-II-17)

### WyomingAgents - Annual Report
- **Billing:** Annual (~May)
- **File name format:** `YYYY-MM-DD-WyomingAgents - Annual Report.pdf`
- **Zoho category:** Legal and Professional Services (C-II-17)

### Biberk Insurance
- **Billing:** Annual (~March)
- **Types:** GL, PL, Umbrella, Workers Comp
- **File name format:** `YYYY-MM-DD-Biberk-[Type].pdf`
- **Zoho category:** Insurance (C-II-15)

### Zoho
- **Billing:** Annual (~April)
- **File name format:** `YYYY-MM-DD-zoho.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)

### Toggl
- **Billing:** Annual (~April)
- **File name format:** `YYYY-MM-DD-toggl.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)

### ChatGPT
- **Billing:** Monthly or annual
- **File name format:** `YYYY-MM-DD-ChatGPT.pdf` or `YYYY-MM-DD-ChatGPT-Teams-Annual.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)

### Squarespace Domains
- **Billing:** Annual (~September/October)
- **File name format:** `YYYY-MM-DD-Squarespace - Domains.pdf`
- **Zoho category:** Office Expense (C-II-18)

### GitHub
- **Billing:** Monthly ~15th (includes Copilot; one month/year also includes annual Pro subscription)
- **File name format:** `YYYY-MM-DD-GitHub.pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)
- **Portal:** github.com/settings/billing → Payment history
- **Receipt location:** Click PDF icon next to transaction to download receipt

### Anthropic
- **Billing:** Monthly ~26th (Claude Max subscription)
- **File name format:** `YYYY-MM-DD-Anthropic-Receipt-[invoice#].pdf`
- **Zoho category:** Software Subscriptions (C-II-27a)
- **Portal:** claude.ai/settings/billing → Invoices section → Click "View"
- **Receipt location:** Opens Stripe invoice page → Click "Download receipt" button
- **Note:** Preserve receipt number from original downloaded filename (e.g., `Receipt-2823-4502-6365.pdf`)

## Ad-hoc Expenses

For one-time purchases (equipment, supplies, travel):
- Use descriptive vendor name
- Include brief description if helpful
- Example: `2024-11-17-Headset-Amazon Order 113-2665686-0520249.pdf`
- **Zoho category:** Supplies (C-II-22) for equipment/hardware
