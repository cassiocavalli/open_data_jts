import re
from typing import Dict, List, Optional

def parse_section_content(content: str) -> List[str]:
    """Parse content into list of keywords/phrases."""
    if not content:
        return []
    
    # Split by '/' and clean up each item
    items = [item.strip() for item in content.split('/')]
    
    # Further split by ',' and ';' and clean up
    result = []
    for item in items:
        sub_items = re.split('[,;]', item)
        result.extend([s.strip() for s in sub_items if s.strip()])
    
    return result

def parse_complementary_info(text: str) -> Optional[Dict[str, List[str]]]:
    """Parse informacoesComplementares into structured format."""
    if not text or text == "null":
        return None
        
    sections = {}
    current_section = None
    current_content = []
    
    # Split text into lines and process each line
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is a section header
        if line.startswith('(') and line.endswith(')'):
            # If we have a previous section, save it
            if current_section:
                sections[current_section] = parse_section_content(' '.join(current_content))
            
            # Start new section
            current_section = re.sub(r'[\(\)]', '', line).strip()
            current_section = ''.join(w.lower().capitalize() for w in current_section.split())
            current_content = []
        else:
            current_content.append(line)
    
    # Save the last section
    if current_section and current_content:
        sections[current_section] = parse_section_content(' '.join(current_content))
    
    return sections