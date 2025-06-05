#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from core.loader import load_template
from core.scanner import run_scan
from core.logger import ResultLogger
from core.module_loader import run_exploit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Ensure all required directories exist"""
    directories = ['results', 'templates', 'modules', 'core']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='PentoScan - Security Scanner')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run a scan')
    scan_parser.add_argument('-t', '--target', required=True, help='Target URL')
    scan_parser.add_argument('-template', '--template', required=True, help='Path to scan template')
    scan_parser.add_argument('-o', '--output', help='Output directory for results')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    setup_directories()
    args = parse_args()
    
    if args.command == 'scan':
        logger.info(f"Starting scan against {args.target} using template {args.template}")
        print("[*] Loading template...")
        template = load_template(args.template)

        print(f"[*] Scanning {args.target} using {template['name']}...")
        scan_result = run_scan(args.target, template)

        # Initialize logger
        logger = ResultLogger(args.output or 'results')
        
        # Run exploit if vulnerable
        exploit_result = None
        if scan_result['vulnerable'] and 'exploit_module' in template:
            print("[*] Running exploit module...")
            exploit_result = run_exploit(template['exploit_module'], args.target, scan_result)

        # Save results
        output_file = logger.save_result(scan_result, exploit_result)
        if output_file:
            print(f"[+] Results saved to {output_file}")

        if scan_result['vulnerable']:
            print("[+] Vulnerability FOUND!")
        else:
            print("[-] Not vulnerable.")
    else:
        logger.error("No command specified")
        sys.exit(1)

if __name__ == '__main__':
    main()
