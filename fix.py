with open('static/groomx_v6.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the {{ problem
content = content.replace(
    "${{'e':'Easy','m':'Medium','a':'Advanced','p':'Pro'}[b.df]}",
    "${getDiffLabel(b.df)}"
)

# Also try the unquoted version
content = content.replace(
    "${{e:'Easy',m:'Medium',a:'Advanced',p:'Pro'}[b.df]}",
    "${getDiffLabel(b.df)}"
)

# Add the helper function
old = "let bCat='all';"
new = """let bCat='all';
function getDiffLabel(df) {
  if (df === 'e') return 'Easy';
  if (df === 'm') return 'Medium';
  if (df === 'a') return 'Advanced';
  if (df === 'p') return 'Pro';
  return df;
}"""
content = content.replace(old, new)

with open('static/groomx_v6.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! Checking for remaining {{ ...')
lines = content.split('\n')
found = False
for i, line in enumerate(lines, 1):
    if '{{' in line:
        print(f'Line {i}: {line.strip()}')
        found = True
if not found:
    print('No {{ found - HTML is clean!')