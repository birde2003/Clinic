# Clinic Invoice System User Manual

## Key Workflows

### 1. Creating a New Invoice
![Create Invoice](screenshots/create-invoice.png)
1. Enter invoice details in the form
2. Click "Save Invoice" 
3. System will validate and store the invoice

### 2. Generating Reports
![Reports](screenshots/generate-report.png)
1. Select report type from dropdown
2. Choose date range
3. Click "Generate Report"
4. Reports saved to `reports/` directory

### 3. Backup Management
![Backup](screenshots/backup-interface.png)
- Automatic daily backups to `backups/`
- Manual backups via "Create Backup" button
- Restore using "Restore Backup" dialog

## Field Descriptions
<!-- SCREENSHOT-PLACEHOLDER: main-interface -->

| Field Name | Description | Data Format |
|------------|-------------|-------------|
| Invoice Number | Unique identifier | YYYY-MM-XXX |
| Date Generated | Invoice creation date | YYYY-MM-DD |
| Payment Method | Payment type used | Cash/Card/Check |
