import re
from typing import Dict, Any, List, Tuple

# Corporate clichés and buzzwords prohibited by the /human skill
CLICHE_PATTERNS = [
    (r'\bresults[- ]driven\b', 'focused on delivery'),
    (r'\bproven track record\b', 'demonstrated history'),
    (r'\bpassionate about\b', 'interested in'),
    (r'\bleverage\b', 'use'),
    (r'\bleveraged\b', 'used'),
    (r'\bleveraging\b', 'using'),
    (r'\bdynamic\b', 'adaptable'),
    (r'\bteam player\b', 'collaborative engineer'),
    (r'\bspearheaded\b', 'led'),
    (r'\bcutting[- ]edge\b', 'modern'),
    (r'\bseasoned\b', 'experienced'),
    (r'\bsynergy\b', 'collaboration'),
    (r'\bsynergies\b', 'efficiencies'),
    (r'\bparadigm\b', 'model'),
    (r'\bdeep dive\b', 'thorough review'),
    (r'\btransformative\b', 'high impact'),
    (r'\butilized\b', 'used'),
    (r'\butilize\b', 'use'),
    (r'\butilizing\b', 'using'),
    (r'\brobust\b', 'resilient'),
    (r'\bseamlessly\b', 'smoothly'),
    (r'\btestament to\b', 'evidence of'),
    (r'\bin order to\b', 'to'),
    (r'\bmultifaceted\b', 'diverse'),
    (r'\bthought leader\b', 'domain specialist'),
    (r'\bgo-getter\b', 'proactive contributor'),
    (r'\bout-of-the-box\b', 'creative'),
    (r'\bstate-of-the-art\b', 'industry standard')
]

HUMAN_SYSTEM_INSTRUCTIONS = """
STRICT WRITING RULES (HUMAN VOICE MANDATE):
1. No corporate clichés or hollow buzzwords: NEVER use "results-driven", "proven track record", "passionate about", "leverage", "dynamic", "team player", "spearhead", "robust", "cutting-edge", "deep dive", or "seasoned".
2. No em-dashes (—) or en-dashes (–). Use standard commas, periods, or semicolons instead.
3. Use active voice and concrete facts: anchor statements in real tools, metrics (latencies, percentages, scale), or precise architecture decisions.
4. Keep sentence rhythms varied. Do not repeat the same sentence opening or formulaic transitions like "Furthermore", "Moreover", "In today's fast-paced environment".
5. Speak directly like a skilled colleague writing to an engineering manager, not a promotional brochure.
"""

def clean_dashes(text: str) -> str:
    """
    Removes em/en dashes and replaces them with standard punctuation or clean spaces.
    """
    if not text:
        return ""
    # Replace em-dashes and en-dashes surrounded by space with comma or semicolon
    text = re.sub(r'\s+[—–]\s+', ', ', text)
    # Replace single em-dashes with comma or hyphen
    text = text.replace('—', ', ')
    text = text.replace('–', '-')
    # Clean any accidental double commas
    text = re.sub(r',\s*,', ',', text)
    # Collapse multiple horizontal spaces while preserving newlines
    text = re.sub(r'[^\S\r\n]{2,}', ' ', text)
    return text

def scrub_cliches(text: str) -> Tuple[str, List[str]]:
    """
    Replaces corporate clichés with natural, direct language.
    Returns (cleaned_text, list_of_replaced_cliches).
    """
    if not text:
        return "", []
    
    cleaned = text
    found_cliches = []
    
    for pattern, replacement in CLICHE_PATTERNS:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            found_cliches.extend([m.lower() for m in matches])
            # Case-preserving or simple replacement
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            
    return cleaned, list(set(found_cliches))

def humanize_text(text: str) -> str:
    """
    Applies the full /human skill pipeline to any generated text.
    """
    if not text:
        return ""
        
    cleaned = clean_dashes(text)
    cleaned, _ = scrub_cliches(cleaned)
    
    # Clean lingering corporate phrasing
    cleaned = re.sub(r'\bIn today\'?s\s+(?:rapidly\s+evolving|fast-paced|competitive)\s+market\b', 'Currently', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bI am excited to submit my application for\b', 'I am writing to apply for', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\bI am confident that my skills make me an ideal fit\b', 'My background aligns directly with what you need', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def validate_humanization(text: str) -> Dict[str, Any]:
    """
    Inspects text to confirm compliance with humanization rules.
    """
    has_em_dash = '—' in text or '–' in text
    cliches_found = []
    for pattern, _ in CLICHE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            cliches_found.extend(matches)
            
    is_compliant = (not has_em_dash) and (len(cliches_found) == 0)
    
    return {
        "is_compliant": is_compliant,
        "has_em_dash": has_em_dash,
        "cliches_found": list(set([c.lower() for c in cliches_found]))
    }
