with open('static/groomx_v6.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
found = []
for i, line in enumerate(lines, 1):
    if '{{' in line:
        found.append(f"Line {i}: {line.strip()}")

if found:
    print(f"Found {len(found)} problems:")
    for f in found:
        print(f)
else:
    print("No {{ found in file")