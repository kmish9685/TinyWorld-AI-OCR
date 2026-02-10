# Project Cleanup Script
# Run this to reduce project size by removing unnecessary files

import os
import shutil

def get_dir_size(path):
    """Calculate directory size in MB"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total += os.path.getsize(filepath)
    return total / (1024 * 1024)  # Convert to MB

def cleanup_project():
    """Remove unnecessary files to reduce project size"""
    
    print("🧹 TinyWorld AI - Project Cleanup")
    print("=" * 50)
    
    # Get initial size
    initial_size = get_dir_size(".")
    print(f"Initial project size: {initial_size:.2f} MB\n")
    
    removed_size = 0
    
    # 1. Remove __pycache__ folders
    print("Removing __pycache__ folders...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            size = get_dir_size(pycache_path)
            shutil.rmtree(pycache_path)
            removed_size += size
            print(f"  ✓ Removed {pycache_path} ({size:.2f} MB)")
    
    # 2. Remove .pyc files
    print("\nRemoving .pyc files...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path) / (1024 * 1024)
                os.remove(file_path)
                removed_size += size
                print(f"  ✓ Removed {file_path}")
    
    # 3. Remove .git folder (if exists and not needed)
    if os.path.exists(".git"):
        response = input("\n⚠️  Remove .git folder? (This removes version history) [y/N]: ")
        if response.lower() == 'y':
            size = get_dir_size(".git")
            shutil.rmtree(".git")
            removed_size += size
            print(f"  ✓ Removed .git folder ({size:.2f} MB)")
    
    # 4. Remove extra demo images (keep only one)
    print("\nChecking for extra demo images...")
    demo_images = [f for f in os.listdir(".") if f.startswith("demo_") and f.endswith((".png", ".jpg", ".jpeg"))]
    if len(demo_images) > 1:
        print(f"  Found {len(demo_images)} demo images. Keeping demo_image.png, removing others...")
        for img in demo_images:
            if img != "demo_image.png":
                size = os.path.getsize(img) / (1024 * 1024)
                os.remove(img)
                removed_size += size
                print(f"  ✓ Removed {img} ({size:.2f} MB)")
    
    # 5. Remove test files
    if os.path.exists("test"):
        response = input("\n⚠️  Remove test folder? [y/N]: ")
        if response.lower() == 'y':
            size = get_dir_size("test")
            shutil.rmtree("test")
            removed_size += size
            print(f"  ✓ Removed test folder ({size:.2f} MB)")
    
    # Final summary
    final_size = get_dir_size(".")
    print("\n" + "=" * 50)
    print(f"✅ Cleanup Complete!")
    print(f"Initial size:  {initial_size:.2f} MB")
    print(f"Removed:       {removed_size:.2f} MB")
    print(f"Final size:    {final_size:.2f} MB")
    print(f"Reduction:     {((initial_size - final_size) / initial_size * 100):.1f}%")
    print("\n💡 Tip: For competition, aim for < 10 MB total size")

if __name__ == "__main__":
    cleanup_project()
