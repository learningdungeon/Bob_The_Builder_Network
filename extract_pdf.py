#!/usr/bin/env python3
"""Extract text from Sentinel Framework PDF"""

try:
    import PyPDF2
    
    with open('The Sentinel Framework.pdf', 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Save to text file
        with open('sentinel_framework_extracted.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Successfully extracted {len(reader.pages)} pages")
        print(f"Total characters: {len(text)}")
        
except ImportError:
    print("PyPDF2 not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyPDF2'])
    print("Please run the script again.")
except Exception as e:
    print(f"Error: {e}")

# Made with Bob
