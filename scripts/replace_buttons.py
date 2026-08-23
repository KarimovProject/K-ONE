import os

templates_dir = r"C:\IEMS\templates"
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            
            replaces = {
                'primary-button': 'btn-primary',
                'secondary-button': 'btn-neutral',
                'ghost-button': 'btn-ghost',
                'text-button': 'btn-ghost',
                'danger-button': 'btn-danger',
                'success-button': 'btn-success',
                'warning-button': 'btn-edit',
            }
            
            for old, new in replaces.items():
                new_content = new_content.replace(f'class="{old}"', f'class="{new}"')
                new_content = new_content.replace(f'class="{old} ', f'class="{new} ')
                new_content = new_content.replace(f' {old}"', f' {new}"')
                new_content = new_content.replace(f' {old} ', f' {new} ')

            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

print("Buttons replaced globally.")
