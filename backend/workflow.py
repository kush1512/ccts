"""
Complete Workflow Script - Carbon Brokers Backend
This script automates the entire process: create project, upload images, monitor, get results
"""

import requests
import json
import time
from pathlib import Path
import sys

# Configuration
BASE_URL = "http://localhost:8000"
IMAGES_FOLDER = r".\data\sample_images"  # Change this to your images folder
PROJECT_NAME = "Forest Carbon Analysis"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

# ============================================================================
# STEP 1: CREATE PROJECT
# ============================================================================
def create_project(name):
    """Create a new project"""
    print_header("STEP 1: Creating Project")
    
    try:
        payload = {"name": name}
        response = requests.post(
            f"{BASE_URL}/projects/",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            project = response.json()
            project_id = project['id']
            print_success(f"Project created successfully!")
            print(f"  Project ID: {Colors.BOLD}{project_id}{Colors.END}")
            print(f"  Name: {project['name']}")
            print(f"  Status: {project['status']}")
            return project_id
        else:
            print_error(f"Failed to create project (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend!")
        print_info("Make sure backend is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return None
    except Exception as e:
        print_error(f"Error creating project: {e}")
        return None

# ============================================================================
# STEP 2: UPLOAD IMAGES
# ============================================================================
def upload_images(project_id, images_folder):
    """Upload images to project"""
    print_header("STEP 2: Uploading Images")
    
    # Check if folder exists
    images_path = Path(images_folder)
    if not images_path.exists():
        print_warning(f"Images folder not found: {images_folder}")
        print_info("Creating sample folder structure...")
        images_path.mkdir(parents=True, exist_ok=True)
        print_warning("Please add your drone images to this folder:")
        print(f"  {images_path.absolute()}")
        return False
    
    # Find image files
    image_files = (
        list(images_path.glob("*.jpg")) +
        list(images_path.glob("*.jpeg")) +
        list(images_path.glob("*.png")) +
        list(images_path.glob("*.tif")) +
        list(images_path.glob("*.tiff"))
    )
    
    if not image_files:
        print_warning(f"No images found in: {images_folder}")
        print_info("Supported formats: .jpg, .jpeg, .png, .tif, .tiff")
        print_warning("Continuing with test data only...")
        return False
    
    print_info(f"Found {len(image_files)} image(s) to upload")
    
    try:
        # Prepare files
        files = []
        for img in image_files:
            print(f"  • {img.name}")
            files.append(('files', open(img, 'rb')))
        
        # Upload
        print_info("Uploading images...")
        response = requests.post(
            f"{BASE_URL}/projects/{project_id}/upload-images/",
            files=files,
            timeout=30
        )
        
        # Close all files
        for _, f in files:
            f.close()
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Images uploaded successfully!")
            print(f"  {result['message']}")
            return True
        else:
            print_error(f"Upload failed (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error uploading images: {e}")
        return False

# ============================================================================
# STEP 3: MONITOR PROCESSING
# ============================================================================
def monitor_processing(project_id, max_wait_seconds=300):
    """Monitor project processing status"""
    print_header("STEP 3: Monitoring Processing")
    
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds
    attempt = 0
    
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/projects/{project_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                project = response.json()
                status = project['status']
                elapsed = int(time.time() - start_time)
                
                attempt += 1
                print(f"[{elapsed:3d}s] Attempt {attempt}: {status}")
                
                if "COMPLETED" in status:
                    print_success("Processing completed successfully!")
                    return True, project
                elif "FAILED" in status:
                    print_error(f"Processing failed: {status}")
                    return False, project
                
                if elapsed > max_wait_seconds:
                    print_warning(f"Timeout after {max_wait_seconds} seconds")
                    print_info("Processing may still be running in background")
                    return None, project
                
                time.sleep(check_interval)
            else:
                print_error(f"Failed to get status (Status: {response.status_code})")
                return False, None
                
        except Exception as e:
            print_error(f"Error checking status: {e}")
            return False, None

# ============================================================================
# STEP 4: DISPLAY RESULTS
# ============================================================================
def display_results(project_id, project_data):
    """Display and save results"""
    print_header("STEP 4: Results Summary")
    
    if not project_data:
        print_error("No project data available")
        return
    
    print(f"Project ID: {Colors.BOLD}{project_id}{Colors.END}")
    print(f"Project Name: {project_data['name']}")
    print(f"Status: {project_data['status']}")
    print(f"CO2 Sequestered: {Colors.BOLD}{project_data['total_co2_tonnes']}{Colors.END} tonnes")
    
    print(f"\nFile Paths:")
    if project_data.get('chm_path'):
        print(f"  • CHM (Canopy Height Model): {project_data['chm_path']}")
    if project_data.get('crowns_path'):
        print(f"  • Tree Crowns (GeoPackage): {project_data['crowns_path']}")
    if project_data.get('carbon_results_path'):
        print(f"  • Carbon Results (CSV): {project_data['carbon_results_path']}")
        
        # Try to read and display CSV results
        try:
            import pandas as pd
            csv_path = project_data['carbon_results_path']
            if Path(csv_path).exists():
                df = pd.read_csv(csv_path)
                print(f"\n📊 Tree Analysis Summary:")
                print(f"  • Total Trees Detected: {len(df)}")
                if 'height_m' in df.columns:
                    print(f"  • Average Tree Height: {df['height_m'].mean():.2f} m")
                if 'crown_area_sqm' in df.columns:
                    print(f"  • Average Crown Area: {df['crown_area_sqm'].mean():.2f} m²")
                if 'co2_sequestered_kg' in df.columns:
                    total_co2 = df['co2_sequestered_kg'].sum() / 1000
                    print(f"  • Total CO2 Sequestered: {total_co2:.2f} tonnes")
                
                print(f"\nFirst 5 trees:")
                print(df.head().to_string())
                
        except ImportError:
            print_warning("Pandas not installed - cannot read CSV results")
        except Exception as e:
            print_warning(f"Could not read results CSV: {e}")

# ============================================================================
# MAIN WORKFLOW
# ============================================================================
def main():
    """Execute complete workflow"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*58 + "╗")
    print("║" + "CARBON BROKERS - COMPLETE WORKFLOW".center(58) + "║")
    print("║" + "Drone Image to Carbon Analysis".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.END}")
    
    # Step 1: Create Project
    project_id = create_project(PROJECT_NAME)
    if not project_id:
        print_error("Cannot continue without project ID")
        sys.exit(1)
    
    # Step 2: Upload Images
    images_uploaded = upload_images(project_id, IMAGES_FOLDER)
    if not images_uploaded:
        print_warning("Continuing without images (test mode)")
    
    # Step 3: Monitor Processing
    success, project_data = monitor_processing(project_id)
    
    if success is None:
        print_info("Processing still running. Check status manually later:")
        print(f"  python -c \"import requests; r = requests.get('http://localhost:8000/projects/{project_id}'); print(r.json())\"")
    elif success:
        # Step 4: Display Results
        display_results(project_id, project_data)
        print_success("Workflow completed successfully!")
    else:
        print_error("Workflow failed during processing")
        print_info("Check project status:")
        print(f"  python -c \"import requests; r = requests.get('http://localhost:8000/projects/{project_id}'); print(r.json())\"")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()
