import pandas as pd
import sys
sys.path.insert(0, r"c:\Users\s.a.gedela\OneDrive - Accenture\Desktop\Knowledge_Bot_V4")

try:
    df = pd.read_excel(r"c:\Users\s.a.gedela\OneDrive - Accenture\Desktop\Knowledge_Bot_V4\uploads\KnowledgeBot_BRD.xlsx", sheet_name=None)
    for sheet, data in df.items():
        print(f"--- {sheet} ---")
        print(data.to_string())
except Exception as e:
    print(f"Error: {e}")
