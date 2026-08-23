import sys

files_to_fix = [
    'templates/accounts/profile.html',
    'static/js/public-calendar.js',
    'templates/events/public_event_detail.html',
    'apps/reporting/selectors.py',
    'static/css/app.css',
    'static/css/calendar.css',
    'static/css/components.css',
    'static/css/motion.css',
    'static/css/tokens.css',
    'templates/master_data/filters.html',
    'templates/partials/topbar.html'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            for line in lines:
                f.write(line.rstrip() + '\n')
        print(f"Fixed {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
