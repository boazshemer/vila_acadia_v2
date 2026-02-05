# Technical Specification

## Tech Stack
- [cite_start]**Frontend:** React (Vite) + Tailwind CSS [cite: 23]
- [cite_start]**Backend:** FastAPI (Python) [cite: 23]
- [cite_start]**Database:** Google Sheets API (via gspread) [cite: 7, 23]
- [cite_start]**Hosting:** Railway [cite: 7, 23]

## Specialized Logic
### Formula Automation
[cite_start]The system must inject the following formulas into the "Totals" section of the Google Sheet[cite: 27, 36]:
- **Total Daily Hours ($H$):** $$H = \sum_{i=1}^{n} h_{i}$$
- **Tip per Hour ($R$):** $$R = \frac{T}{H}$$
- **Employee Payout ($P_i$):** $$P_{i} = h_{i} \times R$$

### Security & Integrity
- [cite_start]**Authentication:** Users verify via 4-digit PIN stored in the "Settings" tab[cite: 11, 23].
- [cite_start]**Race Condition Prevention:** Implementation of "Check-then-Write" logic to ensure single-column creation per date[cite: 33].
- [cite_start]**Manual Overwrite Protection:** System must not overwrite cells containing data[cite: 31, 32].