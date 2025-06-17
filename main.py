#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from core.scanner import run_scan
from core.loader import load_template, load_templates
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
    directories = ['results', 'templates', 'modules', 'core', 'logs']
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
    scan_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    scan_parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available templates')
    
    return parser.parse_args()

def print_scan_result(result):
    """Print scan results in a formatted way"""
    print("\n=== Scan Results ===")
    print(f"Template: {result.template_id}")
    print(f"Author: {result.info.get('author', 'N/A')}")
    print(f"Severity: {result.info.get('severity', 'N/A')}")
    print(f"Tags: {', '.join(result.info.get('tags', []))}")
    print(f"Reference: {result.info.get('reference', 'N/A')}")
    print("\nOverall Status:", "Vulnerable" if result.vulnerable else "Not Vulnerable")
    
    if result.vulnerable:
        print("\nDetailed Results:")
        for req_result in result.results:
            print(f"\nRequest: {req_result['request']['method']} {req_result['request']['url']}")
            print("Status Code:", req_result['response']['status_code'])
            print("Response Headers:")
            for header, value in req_result['response']['headers'].items():
                print(f"  {header}: {value}")
            
            if 'extracted_data' in req_result:
                print("\nExtracted Data:")
                for data in req_result['extracted_data']:
                    print(f"  - {data}")

def main():
    """Main entry point"""
    setup_directories()
    args = parse_args()
    
    # Setup logging level based on verbosity
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    if args.command == 'list':
        templates = load_templates()
        print("\nAvailable Templates:")
        for template in templates:
            print(f"\nID: {template.id}")
            print(f"Name: {template.info.get('name', 'N/A')}")
            print(f"Author: {template.info.get('author', 'N/A')}")
            print(f"Severity: {template.info.get('severity', 'N/A')}")
            print(f"Tags: {', '.join(template.info.get('tags', []))}")
            print(f"Reference: {template.info.get('reference', 'N/A')}")
            print("-" * 50)
    
    elif args.command == 'scan':
        logger.info(f"Starting scan against {args.target} using template {args.template}")
        print(f"[*] Loading template: {args.template}")
        
        template = load_template(args.template)
        if not template:
            print(f"Error: Failed to load template {args.template}")
            sys.exit(1)

        print(f"[*] Scanning {args.target} using {template.info.get('name', 'Unknown')}...")
        scan_result = run_scan(args.target, template)

        # Print results
        print_scan_result(scan_result)

        # Initialize result logger
        result_logger = ResultLogger(args.output or 'results')
        
        # Run exploit if vulnerable
        exploit_result = None
        if scan_result.vulnerable and hasattr(template, 'exploit_module'):
            print("[*] Running exploit module...")
            exploit_result = run_exploit(template.exploit_module, args.target, scan_result)

        # Save results
        output_file = result_logger.save_result(scan_result, exploit_result)
        if output_file:
            print(f"[+] Results saved to {output_file}")
    else:
        logger.error("No command specified")
        sys.exit(1)

if __name__ == '__main__':
    main()
