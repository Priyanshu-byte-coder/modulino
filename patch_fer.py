#!/usr/bin/env python3
"""
Patch FER library to make moviepy import optional.
This fixes the "No module named 'moviepy.editor'" error on Raspberry Pi.
"""

import os
import sys

def patch_fer():
    """Patch FER's classes.py to make moviepy import optional."""
    try:
        import fer
        fer_dir = os.path.dirname(fer.__file__)
        classes_file = os.path.join(fer_dir, 'classes.py')
        
        if not os.path.exists(classes_file):
            print(f"❌ Error: FER classes.py not found at {classes_file}")
            return False
        
        # Read the file
        with open(classes_file, 'r') as f:
            content = f.read()
        
        # Check if already patched
        if 'try:' in content and 'from moviepy.editor import *' in content:
            print("✅ FER is already patched!")
            return True
        
        # Backup original
        backup_file = classes_file + '.backup'
        if not os.path.exists(backup_file):
            with open(backup_file, 'w') as f:
                f.write(content)
            print(f"📦 Backup created: {backup_file}")
        
        # Patch the moviepy import
        old_import = "from moviepy.editor import *"
        new_import = """try:
    from moviepy.editor import *
except ImportError:
    pass  # moviepy not needed for emotion detection"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            # Write patched content
            with open(classes_file, 'w') as f:
                f.write(content)
            
            print("✅ FER successfully patched!")
            print("📝 moviepy import is now optional")
            return True
        else:
            print("⚠️  Warning: Could not find moviepy import to patch")
            print("FER may have been updated. Manual patching required.")
            return False
            
    except ImportError:
        print("❌ Error: FER is not installed")
        return False
    except Exception as e:
        print(f"❌ Error patching FER: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Patching FER library for Raspberry Pi...")
    print()
    
    success = patch_fer()
    
    if success:
        print()
        print("🎉 Patch complete! Testing FER import...")
        try:
            from fer import FER
            detector = FER(mtcnn=False)
            print("✅ FER import successful!")
            print("✅ Emotion detection is ready to use!")
            sys.exit(0)
        except Exception as e:
            print(f"⚠️  FER import test failed: {e}")
            sys.exit(1)
    else:
        print()
        print("❌ Patch failed. Please check the errors above.")
        sys.exit(1)
