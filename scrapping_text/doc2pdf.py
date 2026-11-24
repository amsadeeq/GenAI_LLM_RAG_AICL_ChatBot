# Install dependency if you haven't:
# pip install docx2pdf

import os
from docx2pdf import convert

# Folder containing .docx files
input_folder = "scraped_docs"
output_folder = "scraped_pdfs"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over all .docx files
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".docx"):
        input_path = os.path.join(input_folder, filename)
        # Create output path with same name but .pdf
        output_path = os.path.join(output_folder, filename.replace(".docx", ".pdf"))

        try:
            convert(input_path, output_path)
            print(f"✅ Converted: {input_path} -> {output_path}")
        except Exception as e:
            print(f"❌ Failed to convert {input_path}: {e}")

print("\n🎉 All files processed!")