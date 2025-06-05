import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ResultLogger:
    def __init__(self, output_dir='results'):
        """
        Initialize the result logger
        
        Args:
            output_dir (str): Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def _generate_filename(self, template_id):
        """Generate a timestamped filename for results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{template_id}_{timestamp}.json"
    
    def save_result(self, scan_result, exploit_result=None):
        """
        Save scan and exploit results to a JSON file
        
        Args:
            scan_result (dict): Results from the scan
            exploit_result (dict, optional): Results from the exploit module
        """
        try:
            # Prepare result data
            result_data = {
                'scan': scan_result,
                'timestamp': datetime.now().isoformat(),
            }
            
            if exploit_result:
                result_data['exploit'] = exploit_result
            
            # Generate filename and save
            filename = self._generate_filename(scan_result['template_id'])
            output_path = self.output_dir / filename
            
            with open(output_path, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            logger.info(f"Results saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return None 