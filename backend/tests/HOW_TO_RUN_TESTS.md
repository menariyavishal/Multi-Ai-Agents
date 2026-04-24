# How to Run Researcher Tests Yourself

## Setup (One-time only)
```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend
```

---

## 1️⃣ Run the Demo (See Researcher Logic in Action)
Shows how Researcher analyzes Planner's output and decides which data sources to use.

```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe test_researcher_demo.py
```

**What you'll see:**
- 3 example scenarios (Mobile App, Weather, History)
- For each: Planner's plan → Researcher's analysis → Data sources chosen
- Summary table showing decisions

---

## 2️⃣ Run All Researcher Unit Tests
Tests the Researcher logic with 52 test cases covering all scenarios.

```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_query_analysis.py tests\test_researcher_data_gathering.py tests\test_researcher_workflow.py -v
```

**What you'll see:**
- Test file names
- Individual test results (PASS/FAIL)
- Total count: "52 passed in X.XXs"

**Or run individual test files:**

### Query Analysis Tests (13 tests)
```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_query_analysis.py -v
```

### Data Gathering Tests (19 tests)
```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_data_gathering.py -v
```

### Workflow Tests (20 tests)
```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_workflow.py -v
```

---

## 3️⃣ Quick Syntax Check (No execution)
Verify Python files have correct syntax without running them.

```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m py_compile test_researcher_demo.py
```

---

## 4️⃣ Run Planner Test (See what Planner creates)
Understand the intelligent plans that Researcher will read.

```powershell
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_planner_agent.py -v
```

---

## 📊 Full Workflow Command
Run everything in sequence:

```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend

# 1. Show demo
Write-Host "=== DEMO ===" -ForegroundColor Cyan
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe test_researcher_demo.py

# 2. Run all tests
Write-Host "`n=== TESTS ===" -ForegroundColor Cyan
c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_query_analysis.py tests\test_researcher_data_gathering.py tests\test_researcher_workflow.py -v
```

---

## 🔍 Understanding the Output

### Demo Output Example:
```
✅ Detected Data Type: COMBINED
📡 Data Sources to Use:
   🌐 MCP_SERVERS (Real-time data)
   📊 DATABASE (Historical data)
```
= Researcher read Planner's plan, found both "current" and "historical" keywords → uses both sources

### Test Output Example:
```
test_researcher_query_analysis.py::test_planner_thinks_about_success PASSED
test_researcher_query_analysis.py::test_mobile_app_needs_both_types PASSED
...
52 passed in 0.22s
```
= All 52 tests passed ✅

---

## 🛠️ Troubleshooting

**Command not found?**
- Copy the full path including `\.venv\Scripts\python.exe`
- Don't use just `python` - it might be wrong version

**Module not found (pytest)?**
- First run: `cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend`
- Then run: `c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pip install pytest`

**Tests fail?**
- Check if you're in the `backend` directory
- Verify `.venv` folder exists
- Run demo first to check basic setup works

---

## 📝 Next Steps

Once tests pass ✅:
1. Demo shows the logic works
2. Tests verify all edge cases
3. Then implement real `researcher.py` agent file
4. Update `constants.py` with Groq configuration
5. Create researcher manual test with real Planner outputs

---

## 🚀 Quick Copy-Paste

**I want to see the demo:**
```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend; c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe test_researcher_demo.py
```

**I want to run all tests:**
```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend; c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher_query_analysis.py tests\test_researcher_data_gathering.py tests\test_researcher_workflow.py -v
```

**I want quick summary:**
```powershell
cd c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\backend; c:\Users\HP\OneDrive\Scans\CODES\Python\Multi-Ai-Agents\.venv\Scripts\python.exe -m pytest tests\test_researcher*.py --tb=short
```

