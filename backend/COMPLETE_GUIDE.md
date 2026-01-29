# 🚀 COMPLETE GUIDE - From Images to Carbon Results

## What This System Does

This is a **drone image to carbon sequestration analysis system** that:
1. Takes drone photos of forests
2. Processes them to create 3D models
3. Detects individual trees
4. Calculates their biomass and CO2 sequestration

---

## 📋 PREREQUISITE CHECKLIST

Before starting, verify:

```
✓ Backend running on http://localhost:8000
✓ Python environment configured
✓ Dependencies installed
✓ Database initialized
✓ Data directory created
✓ Drone images ready (optional - can test without images)
```

If not done yet, see **BACKEND_STATUS.md**

---

## ⚡ FASTEST WAY TO GET RESULTS (3 STEPS)

### Step 1: Prepare Images
```powershell
# Create folders for images
mkdir -p .\data\sample_images

# Copy your drone images here
# Supported: .jpg, .png, .tif
# If no images, script will work in test mode
```

### Step 2: Start Backend
```powershell
# Terminal 1 (leave running)
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
$env:PYTHONPATH="c:\Users\jaink\Documents\ML\carbon_brokers\Backend"
C:/Users/jaink/Documents/ML/carbon_brokers/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Run Workflow
```powershell
# Terminal 2
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
python workflow.py
```

**Done!** Results will be in `./data/{project_id}/carbon_inventory.csv`

---

## 📖 DETAILED STEP-BY-STEP GUIDE

### PHASE 1: INITIALIZATION (1 minute)

#### Step 1.1: Open Terminal
```powershell
# Launch PowerShell
```

#### Step 1.2: Navigate to Backend
```powershell
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
```

#### Step 1.3: Configure Environment
```powershell
$env:PYTHONPATH="c:\Users\jaink\Documents\ML\carbon_brokers\Backend"
```

---

### PHASE 2: START SERVER (1 minute)

#### Step 2.1: Start FastAPI
```powershell
C:/Users/jaink/Documents/ML/carbon_brokers/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 2.2: Wait for Confirmation
```
Expected output:
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Step 2.3: Keep Terminal Open
✅ Do NOT close this terminal - it must keep running!

---

### PHASE 3: PREPARE DATA (5-10 minutes)

#### Step 3.1: Create New Terminal
```powershell
# Open new PowerShell window (Terminal 2)
```

#### Step 3.2: Navigate to Data Folder
```powershell
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
```

#### Step 3.3: Create Image Directory
```powershell
mkdir -p .\data\sample_images
```

#### Step 3.4: Add Your Images
```
Copy your drone images to:
  ./data/sample_images/

Supported formats:
  - *.jpg (JPEG images)
  - *.png (PNG images)  
  - *.tif (GeoTIFF rasters)

Example:
  ./data/sample_images/drone_001.jpg
  ./data/sample_images/drone_002.jpg
  ./data/sample_images/drone_003.jpg
```

**No images?** No problem! The system works in test mode with placeholder data.

---

### PHASE 4: RUN ANALYSIS (30 seconds - 2 minutes)

#### Step 4.1: Execute Workflow
```powershell
python workflow.py
```

#### Step 4.2: Watch Progress
```
Expected output:
✓ Project created successfully!
  Project ID: 1
  
✓ Images uploaded successfully!

[0s] Status: PROCESSING: PHOTOGRAMMETRY
[5s] Status: PROCESSING: GENERATING CHM
[10s] Status: PROCESSING: SEGMENTING TREES
[15s] Status: PROCESSING: CALCULATING CARBON

✓ Processing completed successfully!

Project: My Forest Project
Total CO2 Sequestered: 125.45 tonnes
```

---

### PHASE 5: ANALYZE RESULTS (2 minutes)

#### Step 5.1: View Results in Terminal
Results displayed automatically by `workflow.py`:
```
📊 Tree Analysis Summary:
  • Total Trees Detected: 2456
  • Average Tree Height: 18.5 m
  • Average Crown Area: 65.3 m²
  • Total CO2 Sequestered: 125.45 tonnes

First 5 trees:
  tree_id  height_m  crown_area_sqm  estimated_dbh_cm  ...  co2_sequestered_kg
  1        25.5      120.3           7.75              ...  3237.2
  2        22.1      95.6            6.63              ...  2538.0
```

#### Step 5.2: View Detailed CSV
```powershell
# Open detailed results
Invoke-Item .\data\1\carbon_inventory.csv
```

CSV columns:
```
tree_id - Unique identifier for each tree
height_m - Tree height in meters
crown_area_sqm - Crown area in square meters
estimated_dbh_cm - Diameter at breast height
agb_kg - Above-ground biomass
total_biomass_kg - Total biomass (AGB + BGB)
carbon_kg - Carbon content
co2_sequestered_kg - CO2 equivalent
```

#### Step 5.3: Check Other Outputs
```powershell
# List all outputs
dir .\data\1\

# View files:
# - carbon_inventory.csv    Main results
# - tree_crowns.gpkg        Spatial boundaries (GIS format)
# - chm.tif                 3D height model
# - dsm.tif                 Surface model
```

---

## 🔧 MANUAL OPERATIONS (If you want control)

### Create Project Manually
```powershell
python << 'EOF'
import requests

# Create project
response = requests.post(
    "http://localhost:8000/projects/",
    json={"name": "Manual Test Project"}
)

project = response.json()
print(f"✓ Project created: ID = {project['id']}")
EOF
```

### Upload Images Manually
```powershell
python << 'EOF'
import requests
from pathlib import Path

project_id = 1  # Use your project ID
images_folder = r".\data\sample_images"

# Find image files
images = list(Path(images_folder).glob("*.jpg")) + \
         list(Path(images_folder).glob("*.png")) + \
         list(Path(images_folder).glob("*.tif"))

print(f"Found {len(images)} images")

if images:
    # Create file objects
    files = [('files', open(img, 'rb')) for img in images]
    
    # Upload
    response = requests.post(
        f"http://localhost:8000/projects/{project_id}/upload-images/",
        files=files
    )
    
    # Close files
    for _, f in files:
        f.close()
    
    print(f"Upload Status: {response.status_code}")
    print(f"Message: {response.json()['message']}")
EOF
```

### Monitor Status Manually
```powershell
python << 'EOF'
import requests
import time

project_id = 1

for attempt in range(12):  # Check for 60 seconds
    response = requests.get(f"http://localhost:8000/projects/{project_id}")
    project = response.json()
    
    print(f"Attempt {attempt}: {project['status']}")
    
    if "COMPLETED" in project['status']:
        print(f"\n✓ Done! CO2: {project['total_co2_tonnes']} tonnes")
        break
    
    time.sleep(5)
EOF
```

---

## 📊 UNDERSTANDING THE RESULTS

### Key Metrics

**CO2 Sequestered**
- Total: Sum of all trees' carbon content
- Per tree: Individual tree contribution
- Unit: Tonnes (1 tonne = 1000 kg)

**Tree Dimensions**
- Height: Meter
- Crown Area: Square meter (how wide the tree canopy is)
- DBH (Diameter at Breast Height): Centimeters (standard forestry measure)

**Biomass**
- AGB: Above-Ground Biomass (trunk, branches, leaves)
- BGB: Below-Ground Biomass (roots)
- Total: AGB + BGB

### Using Results in GIS

The `tree_crowns.gpkg` file contains vector data that can be opened in:
- QGIS (free)
- ArcGIS
- Any GIS-compatible software

It includes:
- Tree crown polygons
- Geographical coordinates
- Tree attributes

---

## 🎯 COMMON TASKS

### Export Results to Excel
```powershell
python << 'EOF'
import pandas as pd

# Read CSV
df = pd.read_csv('./data/1/carbon_inventory.csv')

# Export to Excel
df.to_excel('./data/1/carbon_results.xlsx', index=False)
print("✓ Saved to: ./data/1/carbon_results.xlsx")
EOF
```

### Create Summary Report
```powershell
python << 'EOF'
import pandas as pd

df = pd.read_csv('./data/1/carbon_inventory.csv')

summary = f"""
CARBON SEQUESTRATION REPORT
===========================
Project: My Forest
Analysis Date: 2026-01-29

STATISTICS
----------
Total Trees: {len(df)}
Avg Height: {df['height_m'].mean():.2f} m
Avg Crown Area: {df['crown_area_sqm'].mean():.2f} m²
Avg DBH: {df['estimated_dbh_cm'].mean():.2f} cm

BIOMASS & CARBON
----------------
Total AGB: {df['agb_kg'].sum()/1000:.2f} tonnes
Total Biomass: {df['total_biomass_kg'].sum()/1000:.2f} tonnes
Total Carbon: {df['carbon_kg'].sum()/1000:.2f} tonnes
Total CO2 Equivalent: {df['co2_sequestered_kg'].sum()/1000:.2f} tonnes

HEIGHT DISTRIBUTION
-------------------
Min: {df['height_m'].min():.2f} m
Max: {df['height_m'].max():.2f} m
Median: {df['height_m'].median():.2f} m
Std Dev: {df['height_m'].std():.2f} m
"""

print(summary)

# Save report
with open('./data/1/report.txt', 'w') as f:
    f.write(summary)
EOF
```

### Visualize Tree Heights
```powershell
python << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('./data/1/carbon_inventory.csv')

# Create histogram
plt.figure(figsize=(12, 6))
plt.hist(df['height_m'], bins=50, color='green', alpha=0.7)
plt.xlabel('Height (meters)')
plt.ylabel('Number of Trees')
plt.title('Tree Height Distribution')
plt.grid(True, alpha=0.3)
plt.savefig('./data/1/height_distribution.png')
print("✓ Chart saved to: ./data/1/height_distribution.png")
EOF
```

---

## 🐛 TROUBLESHOOTING

### Problem: "Connection refused"
**Cause**: Backend not running
**Solution**: 
1. Make sure Terminal 1 still has backend running
2. Check for errors in Terminal 1 output
3. Restart backend if needed

### Problem: "No images found"
**Cause**: Images not in correct folder
**Solution**:
1. Check path: `./data/sample_images/`
2. Verify file formats: .jpg, .png, .tif
3. Copy files and try again
4. Can still test without images (simulated data)

### Problem: "Processing never completes"
**Cause**: Missing dependencies or background task not running
**Solution**:
1. Check Backend logs (Terminal 1)
2. Ensure all dependencies installed
3. Try with fewer/smaller images
4. Restart backend

### Problem: "Database error"
**Cause**: Database corrupted or locked
**Solution**:
```powershell
# Delete and recreate database
rm .\carbon_project.db

# Restart backend
```

---

## 📞 SUPPORT

### Check Backend Status
```powershell
python test_backend.py
```

### View All API Endpoints
```
Open browser: http://localhost:8000/docs
```

### Check Database
```powershell
# View database contents
python << 'EOF'
import sqlite3
conn = sqlite3.connect('./carbon_project.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM projects")
for row in cursor.fetchall():
    print(row)
EOF
```

### View Logs
- Backend logs: Terminal 1 (where uvicorn runs)
- Workflow logs: Terminal 2 (where workflow.py runs)

---

## ✨ OPTIMIZATION TIPS

1. **Use high-quality drone images** (4K resolution recommended)
2. **Ensure good overlap** between drone photos (60%+ overlap)
3. **Clear weather conditions** for best results
4. **Multiple flight patterns** (grid + perimeter)
5. **Lower flight altitude** for better detail (30-50m)

---

## 🎓 LEARNING RESOURCES

**Inside the Backend:**
- `app/main.py` - API endpoints
- `app/models.py` - Database schema
- `app/schemas.py` - Data validation
- `app/tasks.py` - Processing pipeline

**Documentation:**
- `WORKFLOW_GUIDE.md` - Detailed workflow
- `SYSTEM_FLOW.md` - Architecture diagrams
- `QUICK_START.md` - Quick reference
- `BACKEND_STATUS.md` - System status

---

## 🚀 NEXT STEPS

1. ✅ Run the workflow with test data
2. 📸 Add your own drone images
3. 📊 Analyze the results in Excel/GIS
4. 🔄 Run multiple projects
5. 🌍 Integrate with frontend (coming soon)
6. ☁️ Deploy to cloud (Docker support available)

---

## ⚙️ ADVANCED CONFIGURATION

### Change Parameters
Edit `app/tasks.py` to adjust:
```python
MAX_REALISTIC_TREE_HEIGHT_M = 50.0
MAX_REALISTIC_CROWN_AREA_SQM = 500.0
MIN_REALISTIC_TREE_HEIGHT_M = 0.5
MIN_REALISTIC_CROWN_AREA_SQM = 0.5
```

### Change API Port
```powershell
# Use different port (e.g., 8080)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Enable Detailed Logging
```powershell
# Add --log-level debug
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

---

## 📝 QUICK REFERENCE

| Task | Command |
|------|---------|
| Start Backend | `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Run Workflow | `python workflow.py` |
| Test Backend | `python test_backend.py` |
| View API Docs | http://localhost:8000/docs |
| View Results | `./data/{project_id}/carbon_inventory.csv` |
| View Images | `./data/sample_images/` |

---

## ✅ YOU'RE READY!

You now have everything you need to:
1. Upload drone images
2. Analyze them for carbon sequestration
3. Get detailed tree-by-tree results
4. Export data for GIS analysis

**Happy analyzing! 🌍📊**
