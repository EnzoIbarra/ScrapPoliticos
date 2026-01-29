import json
from pathlib import Path

def diagnose_contacts():
    f = Path("data/valid_results.json")
    if not f.exists():
        print("No valid results file.")
        return

    with open(f, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_people = 0
    total_emails = 0
    total_political = 0
    total_political_with_email = 0

    political_keywords = ["alcalde", "alcaldesa", "concejal", "concejala", "teniente"]

    for item in data:
        for p in item.get('data', []):
            name = p.get('nombre', 'Unknown')
            cargo = p.get('cargo')
            cargo = cargo.lower() if cargo else ""
            email = p.get('email')
            
            total_people += 1
            if email:
                total_emails += 1

            is_political = any(k in cargo for k in political_keywords)
            if is_political:
                total_political += 1
                if email:
                    total_political_with_email += 1
                    
    print(f"--- Diagnostic ---")
    print(f"Total Entries: {total_people}")
    print(f"Total with Email: {total_emails} ({total_emails/total_people*100:.1f}%)")
    print(f"Total Political (Alcalde/Concejal): {total_political}")
    print(f"Political WITH Email: {total_political_with_email} ({total_political_with_email/max(1,total_political)*100:.1f}%)")

if __name__ == "__main__":
    diagnose_contacts()
