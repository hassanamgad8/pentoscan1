#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def setup_test_env():
    """Setup test environment"""
    # Create test directories
    Path('test/results').mkdir(exist_ok=True)
    
    # Copy template to test directory
    template_path = Path('templates/lfi_test.yaml')
    test_template_path = Path('test/lfi_test.yaml')
    if template_path.exists():
        with open(template_path, 'r') as src, open(test_template_path, 'w') as dst:
            dst.write(src.read())

def run_php_server():
    """Start PHP development server"""
    php_path = 'php'  # Make sure PHP is in your PATH
    server_cmd = [php_path, '-S', 'localhost:8000', '-t', 'test']
    
    try:
        # Start PHP server in background
        server = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return server
    except Exception as e:
        print(f"Failed to start PHP server: {e}")
        sys.exit(1)

def run_pentoscan():
    """Run PentoScan against test server"""
    scan_cmd = [
        sys.executable,
        'main.py',
        'scan',
        '-t', 'http://localhost:8000',
        '-template', 'test/lfi_test.yaml',
        '-o', 'test/results'
    ]
    
    try:
        result = subprocess.run(
            scan_cmd,
            capture_output=True,
            text=True
        )
        print("\nPentoScan Output:")
        print(result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
    except Exception as e:
        print(f"Failed to run PentoScan: {e}")

def main():
    print("Setting up test environment...")
    setup_test_env()
    
    print("\nStarting PHP test server...")
    server = run_php_server()
    
    try:
        print("\nRunning PentoScan...")
        run_pentoscan()
        
        print("\nTest completed. Check test/results/ for output files.")
    finally:
        print("\nStopping PHP server...")
        server.terminate()
        server.wait()

if __name__ == '__main__':
    main() 