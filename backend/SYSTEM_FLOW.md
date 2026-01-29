# Carbon Brokers - System Architecture & Data Flow

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR COMPUTER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FASTAPI BACKEND (Port 8000)                 │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │         REST API Endpoints                          │ │   │
│  │  │ • POST   /projects/                                 │ │   │
│  │  │ • GET    /projects/{id}                             │ │   │
│  │  │ • POST   /projects/{id}/upload-images/              │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                          ↓                                  │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │         SQLite Database                             │ │   │
│  │  │ • carbon_project.db                                 │ │   │
│  │  │ • Stores: Projects, Status, Results                 │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                            │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │      Celery Tasks (Background Processing)           │ │   │
│  │  │ • Photogrammetry                                    │ │   │
│  │  │ • CHM Generation                                    │ │   │
│  │  │ • Tree Segmentation                                 │ │   │
│  │  │ • Carbon Calculation                                │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              DATA DIRECTORY                              │   │
│  │  ./data/                                                 │   │
│  │  ├── {project_id}/                                       │   │
│  │  │   ├── raw_images/          (input)                   │   │
│  │  │   ├── dsm.tif              (process)                 │   │
│  │  │   ├── chm.tif              (process)                 │   │
│  │  │   ├── tree_crowns.gpkg     (output)                  │   │
│  │  │   └── carbon_inventory.csv (output)                  │   │
│  │  └── sample_odm_outputs/      (test data)               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DATA FLOW DIAGRAM

```
USER (Python/Terminal)
    │
    ├─→ POST /projects/ (Create)
    │   │
    │   └─→ 📦 FastAPI receives request
    │       │
    │       └─→ 💾 Create database record
    │           │
    │           └─→ 📁 Create folders: ./data/{project_id}/
    │               │
    │               └─→ Return Project ID
    │
    │
    ├─→ POST /projects/{id}/upload-images/ (Upload)
    │   │
    │   └─→ 📦 FastAPI receives files
    │       │
    │       └─→ 💾 Save to ./data/{project_id}/raw_images/
    │           │
    │           └─→ 📋 Update status to "ACCEPTED"
    │               │
    │               └─→ 🚀 Kick off Celery task chain
    │
    │
    ├─→ Processing Pipeline (Background/Async)
    │   │
    │   ├─→ 1️⃣  run_photogrammetry()
    │   │   └─→ Generate DSM from images
    │   │
    │   ├─→ 2️⃣  generate_chm()
    │   │   └─→ Create Canopy Height Model
    │   │
    │   ├─→ 3️⃣  segment_trees()
    │   │   └─→ Delineate individual tree crowns
    │   │
    │   └─→ 4️⃣  calculate_carbon()
    │       └─→ Estimate biomass & CO2
    │
    │
    └─→ GET /projects/{id} (Check Status & Results)
        │
        └─→ 📦 FastAPI returns project data
            │
            └─→ ✓ Status (PENDING, PROCESSING, COMPLETED, FAILED)
                ✓ Results (CO2 tonnage, file paths)
```

---

## 🔄 WORKFLOW EXECUTION FLOW

```
START
  │
  ├─ [Step 1] Create Project
  │  └─ Input: Project name
  │  └─ Output: Project ID
  │
  ├─ [Step 2] Upload Images
  │  └─ Input: Image files from folder
  │  └─ Output: Upload confirmation
  │
  ├─ [Step 3] Processing (Background)
  │  │
  │  ├─ Photogrammetry
  │  │  └─ Raw images → DSM (Digital Surface Model)
  │  │
  │  ├─ CHM Generation
  │  │  └─ DSM → CHM (Canopy Height Model)
  │  │
  │  ├─ Tree Segmentation
  │  │  └─ CHM → Tree crowns (Polygons)
  │  │
  │  └─ Carbon Calculation
  │     └─ Crowns + Heights → Biomass → CO2
  │
  ├─ [Step 4] Monitor Status
  │  └─ Poll: GET /projects/{id}
  │  └─ Wait for: COMPLETED or FAILED
  │
  └─ [Step 5] Get Results
     │
     ├─ Project API response:
     │  ├─ total_co2_tonnes (number)
     │  ├─ chm_path (file path)
     │  ├─ crowns_path (file path)
     │  └─ carbon_results_path (CSV file)
     │
     └─ Files in ./data/{project_id}/:
        ├─ carbon_inventory.csv (detailed results)
        ├─ tree_crowns.gpkg (spatial data)
        └─ *.tif (raster data)

END
```

---

## 📥 INPUT FORMATS

**Images (Drone Data):**
```
Supported: .jpg, .png, .tif, .tiff
Format: RGB or Multispectral
Use Case: Aerial/drone imagery of forest
```

**File Structure:**
```
./data/
├── {project_id}/
│   └── raw_images/
│       ├── image_001.jpg
│       ├── image_002.jpg
│       └── image_003.jpg
```

---

## 📤 OUTPUT FORMATS

**CSV Results (carbon_inventory.csv):**
```
tree_id,height_m,crown_area_sqm,estimated_dbh_cm,agb_kg,total_biomass_kg,carbon_kg,co2_sequestered_kg
1,25.5,120.3,7.75,1250.5,1876.0,881.8,3237.2
2,22.1,95.6,6.63,980.2,1470.3,691.0,2538.0
3,31.2,145.8,9.36,1650.8,2476.2,1162.8,4271.8
...
```

**GeoPackage (tree_crowns.gpkg):**
```
Spatial format with:
- Tree crown polygons
- Geometry (coordinates)
- Attributes (tree_id, height, crown_area)
- CRS (Coordinate Reference System)
```

**Raster Files (*.tif):**
```
- dsm.tif: Digital Surface Model
- chm.tif: Canopy Height Model
- dsm_low_res.tif: Downsampled DSM
- dtm.tif: Digital Terrain Model
```

---

## 💻 TERMINAL COMMANDS REFERENCE

```
┌─────────────────────────────────────────────────────┐
│  Terminal 1: START BACKEND (Keep Running)           │
├─────────────────────────────────────────────────────┤
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
$env:PYTHONPATH="c:\Users\jaink\Documents\ML\carbon_brokers\Backend"
C:/Users/jaink/Documents/ML/carbon_brokers/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Terminal 2: RUN WORKFLOW                           │
├─────────────────────────────────────────────────────┤
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
python workflow.py
└─────────────────────────────────────────────────────┘
```

---

## 🎯 QUICK OPERATIONS

### Create Project Only
```python
import requests
r = requests.post("http://localhost:8000/projects/", json={"name": "Test"})
project_id = r.json()['id']
print(f"Project ID: {project_id}")
```

### Check Project Status
```python
import requests
r = requests.get("http://localhost:8000/projects/1")
project = r.json()
print(f"Status: {project['status']}")
print(f"CO2: {project['total_co2_tonnes']} tonnes")
```

### Get All Project Details
```python
import requests
r = requests.get("http://localhost:8000/projects/1")
import json
print(json.dumps(r.json(), indent=2))
```

---

## 📊 EXPECTED PROCESSING TIMES

| Step | Duration | Notes |
|------|----------|-------|
| Create Project | < 1 second | Instant |
| Upload Images | Depends on size | ~1-5 seconds per MB |
| Photogrammetry | 5-30 seconds | Simulated in test mode |
| CHM Generation | 2-10 seconds | Depends on image resolution |
| Tree Segmentation | 5-20 seconds | Watershed algorithm |
| Carbon Calculation | 2-5 seconds | Final computation |
| **Total** | **20-70 seconds** | Varies by data size |

---

## ✅ VALIDATION CHECKLIST

Before uploading images, ensure:

```
✓ Backend is running on http://localhost:8000
✓ Project created successfully (has ID)
✓ Images are in supported format (.jpg, .png, .tif)
✓ Images folder exists and contains files
✓ File permissions are correct
✓ SQLite database exists (./carbon_project.db)
✓ ./data/ directory exists
```

After processing:

```
✓ Status changed from "PROCESSING" to "COMPLETED"
✓ total_co2_tonnes is not null
✓ carbon_results_path file exists
✓ CSV contains tree data
✓ Results folder has all output files
```

---

## 🔗 USEFUL LINKS

- API Interactive Docs: http://localhost:8000/docs
- Backend Logs: Terminal 1 (where uvicorn is running)
- Database: `./carbon_project.db` (SQLite)
- Results: `./data/{project_id}/carbon_inventory.csv`

---

## 📝 NOTES

- Results are saved immediately after upload completes
- Processing happens asynchronously (in background)
- Check status regularly with GET /projects/{id}
- All temporary files are in ./data/ directory
- Database persists between runs
