import glob
import re

svg_view = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
svg_edit = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def replacer(match):
        inner = match.group(1)
        
        # Replace View
        inner = re.sub(r'<a([^>]+href="[^"]+")>(?:{% trans "View" %}|{%\s*trans\s*"Ko‘rish"\s*%})</a>',
                       f'<a class="btn-ghost btn-icon compact"\\1 title=\'{{% trans "View" %}}\'>{svg_view}</a>', inner)
        
        # Replace Edit
        inner = re.sub(r'<a([^>]+href="[^"]+")>(?:{% trans "Edit" %}|{%\s*trans\s*"Tahrirlash"\s*%})</a>',
                       f'<a class="btn-ghost btn-icon compact"\\1 title=\'{{% trans "Edit" %}}\'>{svg_edit}</a>', inner)

        return f'<td style="text-align: right;"><div class="table-actions" style="display: flex; gap: 4px; justify-content: flex-end;">{inner}</div></td>'

    new_content = re.sub(r'<td class="table-actions">(.*?)</td>', replacer, content, flags=re.DOTALL)
    
    # Also fix table header to match right-align
    new_content = re.sub(r'<th><span class="sr-only">{% trans "Actions" %}</span></th>', r'<th style="text-align: right;">{% trans "Actions" %}</th>', new_content)
    
    # Quick fix for any broken tags that currently have \"
    new_content = new_content.replace(r'\"View\"', '"View"').replace(r'\"Edit\"', '"Edit"')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

files = glob.glob('C:/IEMS/templates/**/*list*.html', recursive=True)
for f in files:
    if 'event_list.html' not in f and 'admin' not in f:
        process_file(f)
