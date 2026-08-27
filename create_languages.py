import json
import os

# Create locales directory if it doesn't exist
if not os.path.exists('locales'):
    os.makedirs('locales')

# Load English translations
with open('locales/en.json', 'r', encoding='utf-8') as f:
    en_translations = json.load(f)

# All supported languages
languages = [
    'hi', 'bn', 'ta', 'te', 'mr', 'gu', 'pa', 'kn', 'ml', 
    'ur', 'ne', 'id', 'es', 'fr', 'de', 'ru', 'tr', 'pt', 
    'ar', 'ja', 'ko', 'zh'
]

# Create language files
for lang in languages:
    file_path = f'locales/{lang}.json'
    
    # Check if file already exists
    if os.path.exists(file_path):
        print(f"✅ {file_path} already exists")
        continue
    
    # Create file with English translations as placeholder
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(en_translations, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Created {file_path}")

print("\n🎉 All language files created successfully!")
print("Now you can translate each file by updating the values.")
