# PROJECT: Photocopy Counter Agent

## 1. SYSTEM OVERVIEW

This is a Python desktop application (PySide6) used to:
- Collect counter data from photocopy machines
- Parse HTML data
- Store results in SQLite
- Display in UI

Architecture:
- core → fetch + parse
- services → orchestration
- database → SQLite
- ui → PySide6

---

## 2. CORE DATA FLOW

machine.method_code
    ↓
data_method
    ↓
- data_url
- parser_method (requests / selenium)
- counter_method (parser file)
    ↓
url = http://<ip><data_url>
    ↓
fetch HTML
    ↓
parse via parser
    ↓
save to DB

---

## 3. DATABASE DESIGN

### machine
- ip (stored in serial currently)
- method_code
- data_url (optional cache)

### data_method
- code
- data_url
- parser_method → fetch type
- counter_method → parser file name

### counter_log
- machine_id
- timestamp
- total, bw, color, copy, printer, scan
- raw HTML

---

## 4. PARSER SYSTEM

### Rule:
counter_method = module name

Example:
counter_method = "RicohIM4000"

→ file:
core/parsers/RicohIM4000.py

### Required interface:
```python
def parse(raw: str) -> dict:
Output format:
{
  "total": int,
  "bw": int,
  "color": int,
  "copy": int,
  "printer": int,
  "scan": int
}
5. FETCH SYSTEM

parser_method defines how to fetch:

"requests" → use requests
"selenium" → use Selenium

DO NOT:

hardcode brand (Ricoh, Toshiba)
use string matching
6. ENGINE RULE

Engine must:

Load machine
Load data_method
Build URL
Fetch HTML
Call parser dynamically
Save result
7. CODING RULES
No index access (machine[5])
Use dict:
machine["ip"]
No hardcode parser
No business logic in UI
No DB call in parser
Function < 50 lines
Always log errors
8. DYNAMIC IMPORT
import importlib

module = importlib.import_module(f"core.parsers.{counter_method}")
result = module.parse(raw)
9. ERROR HANDLING
Never use bare except
Always log error
Return safe default
10. DO NOT
Do not modify DB schema randomly
Do not duplicate parser logic
Do not fetch inside parser
Do not use static mapping
11. DEVELOPMENT TASK TEMPLATE
Fix bug
Fix bug:

File: <file>

Problem:
<describe>

Requirements:
- find root cause
- minimal change

Return:
- updated code
Add feature
Add feature:

Feature:
<describe>

Requirements:
- follow architecture
- no breaking change

Return:
- code only
Refactor
Refactor:

Goals:
- clean code
- reduce duplication

Return:
- updated code
12. PRIORITY
Data accuracy
Clean architecture
Modular design
DB-driven logic
13. IMPORTANT NOTE

System is DB-driven:

parser is NOT based on brand
everything comes from data_method