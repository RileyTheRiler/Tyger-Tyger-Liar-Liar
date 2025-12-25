import sys
import os
from pathlib import Path

# Add project root to path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.content.schema_validator import run_validation

def main():
    content_dir = root_dir / "data"
    schemas_dir = root_dir / "schemas"
    
    success = run_validation(str(content_dir), str(schemas_dir))
    
    if success:
        print("\n[SUCCESS] Content validation passed.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Content validation failed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
