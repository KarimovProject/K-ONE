import re

diff = open('temp_diff.patch', 'r', encoding='utf-16').read()
lines = diff.splitlines()

bad_renames = []
for l in lines:
    if l.startswith('+') and 'K-ONE' in l:
        # check if it's in a class, id, data-, url, or block
        match = re.search(r'(id=|class=|data-|aria-|href=|src=|{% url|{% block|name=)[\'"]?[a-zA-Z0-9_\-\s]*K-ONE', l, re.I)
        if match:
            bad_renames.append(l)

with open('bad_renames.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(bad_renames))
