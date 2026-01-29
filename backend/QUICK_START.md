# QUICK START - Copy & Paste Commands

## Terminal 1: Start Backend Server

```powershell
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
$env:PYTHONPATH="c:\Users\jaink\Documents\ML\carbon_brokers\Backend"
C:/Users/jaink/Documents/ML/carbon_brokers/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ Keep this running! Don't close this terminal.

---

## Terminal 2: Run Complete Workflow

```powershell
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
python workflow.py
```

This will:
1. ✓ Create a new project
2. ✓ Upload images (if available)
3. ✓ Monitor processing
4. ✓ Display results

---

## Manual Commands (If you want to do it step-by-step)

### Create Project
```powershell
python << 'EOF'
import requests
response = requests.post("http://localhost:8000/projects/", json={"name": "My Project"})
project = response.json()
print(f"Project ID: {project['id']}")
EOF
```

### Upload Images
```powershell
# First, add your images to: ./data/sample_images/

python << 'EOF'
import requests
from pathlib import Path

project_id = 1  # Change to your project ID
images_folder = r".\data\sample_images"

image_files = list(Path(images_folder).glob("*.jpg")) + \
              list(Path(images_folder).glob("*.png"))

if image_files:
    files = [('files', open(img, 'rb')) for img in image_files]
    response = requests.post(
        f"http://localhost:8000/projects/{project_id}/upload-images/",
        files=files
    )
    for _, f in files:
        f.close()
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
EOF
```

### Check Status
```powershell
python << 'EOF'
import requests
project_id = 1  # Change to your project ID
response = requests.get(f"http://localhost:8000/projects/{project_id}")
project = response.json()
print(f"Status: {project['status']}")
print(f"CO2: {project['total_co2_tonnes']} tonnes")
EOF
```

---

## View API Documentation

Open in browser:
```
http://localhost:8000/docs
```

This shows all available endpoints with interactive testing.

---

## File Locations

**All results saved in:**
```
./data/{project_id}/
├── raw_images/              # Your uploaded images
├── chm.tif                 # Canopy Height Model
├── tree_crowns.gpkg        # Tree crown polygons
└── carbon_inventory.csv    # Results
```

---

## Troubleshooting

### Backend won't start
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <PID> /F
```

### Connection refused
- Ensure backend is running in Terminal 1
- Check firewall settings
- Try: `ping localhost`

### Images not uploading
- Check folder exists: `.\data\sample_images\`
- Ensure images are .jpg, .png, or .tif format
- Check file permissions

---

## API Endpoints Summary

| Method | URL | Purpose |
|--------|-----|---------|
| GET | `http://localhost:8000/docs` | View all endpoints |
| POST | `http://localhost:8000/projects/` | Create project |
| GET | `http://localhost:8000/projects/1` | Get project details |
| POST | `http://localhost:8000/projects/1/upload-images/` | Upload images |

---

## Complete Example Workflow

```powershell
# 1. Terminal 1: Start backend (keep running)
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
$env:PYTHONPATH="c:\Users\jaink\Documents\ML\carbon_brokers\Backend"
C:/Users/jaink/Documents/ML/carbon_brokers/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Terminal 2: Run workflow
cd c:\Users\jaink\Documents\ML\carbon_brokers\Backend
python workflow.py
```

That's it! The workflow script handles everything.

---

## Next Steps

1. **Add your drone images** to `./data/sample_images/`
2. **Run the workflow**: `python workflow.py`
3. **Check results** in `./data/{project_id}/carbon_inventory.csv`
4. **View documentation**: Open http://localhost:8000/docs

---

## Support

For detailed information, see:
- `WORKFLOW_GUIDE.md` - Complete step-by-step guide
- `BACKEND_STATUS.md` - System status and architecture
- `app/main.py` - API implementation
