import markdown
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else 'output'

with open(f'{filename}.md', 'r') as f:
    text = f.read()

html = markdown.markdown(text)

with open(f'{filename}.html', 'w') as f:
    f.write(html)

