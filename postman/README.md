# Postman Collection Usage Guide

## Import Collection

1. Open Postman
2. Click **Import** button
3. Select `TuniGuard_API_Collection.json`
4. Collection appears in left sidebar

## Setup Environment

1. Create new environment: **TuniGuard Local**
2. Add variables:
   - `base_url`: `http://localhost:5000`
   - `user_id`: `1` (after registration)

## Testing Workflow

### 1. Start Server
```powershell
cd c:\Users\Administrator\Desktop\api\tuniguard
.\venv\Scripts\activate
python run.py
```

### 2. Test Sequence

**A. Create User**
- Run: `User Management > Register User`
- Save `user_id` from response
- Update environment variable

**B. Test Threat Detection**
1. `Threat Detection > Scan SMS - Banking Phishing`
2. `Threat Detection > Scan SMS - Fake Prize`
3. `Threat Detection > Scan SMS - Mobile Money Scam`
4. `Threat Detection > Scan SMS - Safe Message`

**C. Test Batch Processing**
- Run: `Threat Detection > Batch Scan`
- Verify multiple results returned

**D. Test Intelligence**
1. `Threat Intelligence > List All Threats`
2. `Threat Intelligence > Trending Threats - 7 Days`

**E. Test Chatbot**
1. Run a scan first to get `scan_id`
2. `Chatbot > Chat - Ask Question` (update scan_id)
3. `Chatbot > Get Chat History`

**F. Test Analytics**
1. `Analytics > User Analytics - 30 Days`
2. `Analytics > National Analytics`
3. `Analytics > Performance Metrics`

### 3. Verify Health
- Run: `Utility > Health Check`
- Should return: `"status": "online"`

## Sample Test Cases

### Test Case 1: High-Risk Phishing
**Request**: Scan SMS - Banking Phishing  
**Expected**:
- `threat_detected`: true
- `detection_score`: > 90
- `severity`: "Critical"

### Test Case 2: Safe Message
**Request**: Scan SMS - Safe Message  
**Expected**:
- `threat_detected`: false
- `detection_score`: < 30
- `severity`: "Low"

### Test Case 3: Batch Processing
**Request**: Batch Scan  
**Expected**:
- `total_scanned`: 2
- Mixed results (1 threat, 1 safe)

## Automated Testing

### Newman (CLI)
```powershell
npm install -g newman
newman run TuniGuard_API_Collection.json
```

### Collection Runner
1. Select collection
2. Click **Run**
3. Review results

## Tips

- Use **Pre-request Scripts** for dynamic data
- Add **Tests** tab for assertions
- Save **Responses** for documentation
- Use **Environments** for different stages

---

Happy Testing! 🧪
