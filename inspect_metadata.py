import pickle
import os

metadata_path = os.path.join('backend', 'faiss_index', 'metadata.pkl')
if os.path.exists(metadata_path):
    with open(metadata_path, 'rb') as f:
        data = pickle.load(f)
    
    found = False
    for m in data:
        if 'Tanisha' in m.get('sop_name', ''):
            print(f"--- CHUNK FROM: {m['sop_name']} ---")
            print(m['text'])
            print("-" * 30)
            found = True
    
    if not found:
        print("No chunks found for Tanisha's Team.")
else:
    print("Metadata file not found.")
