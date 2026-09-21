import os
import re

files_to_process = [
    'templates/venues/venue_list.html',
    'templates/events/event_type_list.html',
    'templates/events/speaker_list.html',
    'templates/organizations/organization_list.html',
    'templates/organizations/sponsor_list.html',
    'templates/publications/list.html',
    'templates/events/event_list.html',
    'templates/events/approvals.html'
]

SVG_VIEW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
SVG_EDIT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>'
SVG_ACTIVATE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
SVG_DELETE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'

for filepath in files_to_process:
    full_path = os.path.join('C:/IEMS', filepath)
    if not os.path.exists(full_path):
        continue
        
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We will find every action block and replace it.
    # The actions are in either <td class="actions-cell">...</td> or <td style="text-align: right;">...</td>
    
    def replacement(match):
        block = match.group(0)
        
        # Extract URLs
        view_url = None
        edit_url = None
        approve_url = None
        reject_url = None
        
        view_match = re.search(r'href="([^"]+)"[^>]*class="[^"]*action-view[^"]*"', block)
        if not view_match:
            view_match = re.search(r'href="([^"]+)"[^>]*>\s*(<svg[^>]*>.*?</svg>)?\s*\{\%\s*trans\s*[\'"]View[\'"]\s*\%\}', block, re.DOTALL)
        if view_match: view_url = view_match.group(1)
        
        edit_match = re.search(r'href="([^"]+)"[^>]*class="[^"]*action-edit[^"]*"', block)
        if not edit_match:
            edit_match = re.search(r'href="([^"]+)"[^>]*>\s*(<svg[^>]*>.*?</svg>)?\s*\{\%\s*trans\s*[\'"]Edit[\'"]\s*\%\}', block, re.DOTALL)
        if edit_match: edit_url = edit_match.group(1)
        
        approve_match = re.search(r'action="([^"]+)"[^>]*>.*?action-activate', block)
        if approve_match: approve_url = approve_match.group(1)
        
        reject_match = re.search(r'action="([^"]+)"[^>]*>.*?action-delete', block)
        if reject_match: reject_url = reject_match.group(1)
        
        # Build standard replacement
        new_td = '<td class="actions-cell">\n'
        
        # Desktop Dropdown
        new_td += '  <div class="dropdown-wrapper desktop-only" style="display: inline-block; text-align: left;">\n'
        new_td += '    <button type="button" class="btn-ghost btn-icon compact dropdown-toggle" aria-label="{% trans \'Actions\' %}">\n'
        new_td += '      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>\n'
        new_td += '    </button>\n'
        new_td += '    <div class="premium-dropdown-menu" hidden>\n'
        
        if view_url:
            new_td += f'      <a href="{view_url}" class="action-view">{SVG_VIEW} {{% trans "View" %}}</a>\n'
        if edit_url:
            if '{% if can_manage %}' in block:
                new_td += f'      {{% if can_manage %}}\n      <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n      {{% endif %}}\n'
            elif '{% if can_create' in block:
                new_td += f'      {{% if can_create and e.status != \'cancelled\' %}}\n      <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n      {{% endif %}}\n'
            else:
                new_td += f'      <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n'
                
        if approve_url:
            new_td += f'      {{% if nav_key == \'approvals\' %}}\n'
            new_td += f'      <form method="post" action="{approve_url}" style="margin:0;">{{% csrf_token %}}<button type="submit" class="action-activate">{SVG_ACTIVATE} {{% trans "Approve" %}}</button></form>\n'
            new_td += f'      <form method="post" action="{reject_url}" style="margin:0;">{{% csrf_token %}}<button type="submit" class="action-delete">{SVG_DELETE} {{% trans "Reject" %}}</button></form>\n'
            new_td += f'      {{% endif %}}\n'
            
        new_td += '    </div>\n'
        new_td += '  </div>\n'
        
        # Mobile Row
        new_td += '  <div class="mobile-actions-row mobile-only">\n'
        if view_url:
            new_td += f'    <a href="{view_url}" class="action-view">{SVG_VIEW} {{% trans "View" %}}</a>\n'
        if edit_url:
            if '{% if can_manage %}' in block:
                new_td += f'    {{% if can_manage %}}\n    <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n    {{% endif %}}\n'
            elif '{% if can_create' in block:
                new_td += f'    {{% if nav_key != \'approvals\' and can_create and e.status != \'cancelled\' %}}\n    <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n    {{% endif %}}\n'
            else:
                new_td += f'    <a href="{edit_url}" class="action-edit">{SVG_EDIT} {{% trans "Edit" %}}</a>\n'
        
        if approve_url:
            new_td += f'    {{% if nav_key == \'approvals\' %}}\n'
            new_td += f'    <form method="post" action="{approve_url}" style="margin:0; flex: 1 1 0;"><button type="submit" class="action-activate" style="width:100%">{SVG_ACTIVATE} {{% trans "Approve" %}}</button></form>\n'
            new_td += f'    <form method="post" action="{reject_url}" style="margin:0; flex: 1 1 0;"><button type="submit" class="action-delete" style="width:100%">{SVG_DELETE} {{% trans "Reject" %}}</button></form>\n'
            new_td += f'    {{% endif %}}\n'

        new_td += '  </div>\n'
        new_td += '</td>'
        
        return new_td

    new_content = re.sub(r'<td class="actions-cell">.*?</td>', replacement, content, flags=re.DOTALL)
    new_content = re.sub(r'<td style="text-align: right;">\s*<div class="dropdown-wrapper".*?</td>', replacement, new_content, flags=re.DOTALL)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        print(f"Updated {filepath}")
