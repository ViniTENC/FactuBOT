# Invoice Automation Bot

Telegram bot that automates invoice data entry using AI vision. Send a photo or PDF of any invoice and the bot extracts the data, compares prices against purchase history, and logs everything to a spreadsheet — no manual typing required.

## Features

- Accepts invoice photos (including iPhone HEIC) and PDF files
- Extracts supplier, date, invoice number, items, quantities, units, and prices using AI
- Detects price increases compared to previous purchases
- Confirms before saving — keeps humans in the loop
- Logs each line item to Google Sheets for tracking and reporting

## Tech

- Python · python-telegram-bot · Google Gemini API · Google Sheets API

## Usage

1. Send an invoice photo or PDF to the bot
2. Review the extracted data and price alerts
3. Confirm to save or cancel

---

*Built as a real-world automation tool for a business that processes supplier invoices.*
