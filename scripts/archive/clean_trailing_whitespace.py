import os

def clean_all_whitespace():
    target_dirs = ['static', 'templates', 'tests', 'apps', 'config', 'scripts', 'locale']
    cleaned_count = 0
    for d in target_dirs:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(('.css', '.html', '.js', '.py', '.po', '.txt', '.md', '.json')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        new_lines = [line.rstrip() + '\n' for line in lines]
                        if new_lines != lines:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.writelines(new_lines)
                            cleaned_count += 1
                    except Exception as e:
                        pass
    print(f"Cleaned trailing whitespace in {cleaned_count} files.")

if __name__ == '__main__':
    clean_all_whitespace()
