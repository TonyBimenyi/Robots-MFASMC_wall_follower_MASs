import re
import csv

# Paste all your copied text here (or read from file)
raw_text = """
paste everything you copied from the PDF here...
including all pages you have
"""

lines = [line.rstrip() for line in raw_text.splitlines() if line.strip()]

rows = []
current_chapter_nr = ""
current_chapter = ""

i = 0
while i < len(lines):
    line = lines[i]

    # Chapter number + title
    if re.match(r'^\d{2}-\d{1,2}\b', line):
        parts = re.split(r'\s{2,}', line.strip(), maxsplit=1)
        if len(parts) >= 1:
            current_chapter_nr = parts[0]
        if len(parts) >= 2:
            current_chapter = parts[1].strip()
        i += 1
        continue

    # Typical fault line pattern: description ........ code task
    # We look for lines ending with something like  xxx xxx xx   xx-xx TASK xxx
    m = re.search(r'(\d{3}\s*\d{3}\s*\d{2})\s+([\d-]+\s*TASK\s*\d{3})$', line)
    if m:
        code = m.group(1).replace(" ", "")
        task = m.group(2).strip()
        # Everything before the code is description
        desc_part = line[:m.start()].rstrip(' .…-')

        # Try to clean up common patterns
        desc_part = re.sub(r'\s*\.+\s*$', '', desc_part).strip()
        desc_part = re.sub(r'\s{2,}', ' ', desc_part)

        # Very rough fault title = first meaningful phrase
        title = desc_part.split(' ', 4)[:4]
        title = ' '.join(title).strip(' •*-:.')

        rows.append({
            'chapter_number': current_chapter_nr,
            'chapter': current_chapter,
            'fault_title': title,
            'fault_description': desc_part,
            'fault_code': code,
            'task': task
        })
        i += 1
        continue

    # Sub-item continuation (indented or starts with • / -)
    if line.strip().startswith(('•', '-', '·', '*')) or (len(line) > 0 and line[0].isspace()):
        # You can append to previous row's description if you want multi-line
        # For simplicity we skip or treat as new — adjust as needed
        pass

    i += 1

# Save to CSV
with open('faults_cleaned.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['chapter_number','chapter','fault_title','fault_description','fault_code','task'])
    writer.writeheader()
    writer.writerows(rows)

print(f"Extracted {len(rows)} rows")