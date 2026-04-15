#!/usr/bin/env python3
"""
Debug script to inspect MCAP bagfile contents
"""

import sys
from pathlib import Path

try:
    import mcap
    print("✓ mcap library available")
except ImportError:
    print("❌ mcap not installed")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python3 inspect_bag.py <bagfile_path>")
    sys.exit(1)

bag_path = Path(sys.argv[1])
mcap_file = bag_path / f"{bag_path.name}_0.mcap"

if not mcap_file.exists():
    print(f"❌ MCAP file not found: {mcap_file}")
    sys.exit(1)

print(f"Inspecting: {mcap_file}\n")

try:
    with open(mcap_file, 'rb') as f:
        file_bytes = f.read()
        print(f"File size: {len(file_bytes)} bytes")
        print(f"\nSearching for message patterns...\n")
        
        # Look for JSON patterns
        import re
        json_count = 0
        for match in re.finditer(rb'\{[^}]*\}', file_bytes):
            json_count += 1
            if json_count <= 5:  # Show first 5
                try:
                    data = match.group().decode('utf-8', errors='ignore')
                    print(f"JSON {json_count}: {data[:100]}")
                except:
                    print(f"JSON {json_count}: (non-text)")
        
        print(f"\nTotal JSON-like objects found: {json_count}\n")
        
        # Look for topic strings
        topic_patterns = [b'/imu/data', b'/motor/command', b'/motor/status', b'/parameter', b'/rosout']
        for pattern in topic_patterns:
            if pattern in file_bytes:
                print(f"✓ Found topic: {pattern.decode()}")
            else:
                print(f"✗ Missing topic: {pattern.decode()}")
        
        print("\n" + "="*60)
        print("Raw file preview (first 500 bytes as hex):")
        print("="*60)
        print(file_bytes[:500].hex())
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
