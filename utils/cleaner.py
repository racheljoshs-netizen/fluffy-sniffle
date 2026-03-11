import os
import shutil
import random
import time
from pathlib import Path
from PIL import Image

# Aegis Protocol: File System Sanitation
# 3-Pass Overwrite (DoD Short)
PASSES = 3

def secure_delete(file_path):
    """
    Overwrites a file with random bytes before deleting it.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return False
    
    try:
        size = path.stat().st_size
        with open(path, "wb") as f:
            for _ in range(PASSES):
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
        
        os.remove(path)
        print(f"[Cleaner] Securely Wiped: {path.name}")
        return True
    except Exception as e:
        print(f"[Cleaner] Error wiping {path}: {e}")
        return False

def strip_metadata(image_path):
    """
    Removes EXIF/XMP metadata from an image.
    Overwrite the original file with the stripped version.
    """
    path = Path(image_path)
    if not path.exists(): return False

    try:
        with Image.open(path) as img:
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            
            # Save over original without metadata
            clean_img.save(path)
            print(f"[Cleaner] Metadata Stripped: {path.name}")
            return True
    except Exception as e:
        print(f"[Cleaner] Error stripping {path}: {e}")
        return False

def purge_workspace(target_dir):
    """
    Recursively securely deletes a directory.
    """
    target = Path(target_dir)
    if not target.exists(): return

    print(f"[Cleaner] Purging Workspace: {target}")
    
    # Files first
    for file_path in target.glob("**/*"):
        if file_path.is_file():
            secure_delete(file_path)

    # Then folders
    shutil.rmtree(target, ignore_errors=True)
    print(f"[Cleaner] Workspace Vaporized: {target}")

if __name__ == "__main__":
    # Internal Test
    test_file = "test_wipe.txt"
    with open(test_file, "w") as f: f.write("Secret Data")
    
    print("Testing Secure Delete...")
    secure_delete(test_file)
    
    if not os.path.exists(test_file):
        print("Test Passed: File Gone.")
    else:
        print("Test Failed: File Persists.")
