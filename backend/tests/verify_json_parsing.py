import re
import json

def parse_llm_json(raw_response):
    """Replicated logic from interactions.py for testing"""
    try:
        # Try to find JSON block
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            try:
                response_data = json.loads(json_match.group(0))
            except json.JSONDecodeError:
                # If direct parsing fails, try cleaning the match
                cleaned_json = json_match.group(0).replace('\n', '').replace('\r', '')
                # Remove potential trailing commas before closing braces
                cleaned_json = re.sub(r',\s*\}', '}', cleaned_json)
                cleaned_json = re.sub(r',\s*\]', ']', cleaned_json)
                response_data = json.loads(cleaned_json)

            return response_data
        else:
            # Heuristic extraction
            if '"narration":' in raw_response:
                nar_match = re.search(r'"narration":\s*"([^"]*)"', raw_response)
                if nar_match:
                    return {"narration": nar_match.group(1)}
            return {"narration": raw_response}
    except Exception as e:
        return {"narration": raw_response, "error": str(e)}

# Test Cases
test_cases = [
    {
        "name": "Standard JSON",
        "input": '```json\n{"narration": "Hello world", "suggested_actions": ["A", "B"]}\n```',
        "expected": "Hello world"
    },
    {
        "name": "Messy JSON with trailing comma",
        "input": 'Here is the response: {"narration": "Messy", "suggested_actions": ["A", "B"], } Hope you like it!',
        "expected": "Messy"
    },
    {
        "name": "Broken JSON with narration only",
        "input": 'Some text before "narration": "Extracted narration" some text after',
        "expected": "Extracted narration"
    },
    {
        "name": "The User reported case",
        "input": 'Lo sfido\nIl Mondo Risponde:\n```json { "narration": "Ti avventi verso il Dark Mage...", "suggested_actions": ["Attaccare il mago con la tua spada", "Tentare di interrogare il mago per ottenere informazioni"], "event": null, "enemy": "Dark Mage", "suggested_actions": ["Attacca il mago con la tua spada", "Cerca di disarmare il mago"] } ```',
        "expected": "Ti avventi verso il Dark Mage..."
    }
]

for tc in test_cases:
    result = parse_llm_json(tc["input"])
    print(f"Test: {tc['name']}")
    print(f"Result Narration: {result.get('narration')[:30]}...")
    if tc["expected"] in result.get('narration', ''):
        print("✅ PASS")
    else:
        print("❌ FAIL")
    print("-" * 20)
