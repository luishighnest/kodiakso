import os
import hashlib
import zipfile
import shutil
import xml.etree.ElementTree as ET

def get_addon_info(addon_dir):
    addon_xml = os.path.join(addon_dir, 'addon.xml')
    if not os.path.exists(addon_xml):
        return None, None
    tree = ET.parse(addon_xml)
    root = tree.getroot()
    return root.attrib.get('id'), root.attrib.get('version')

def create_zip(addon_dir, target_dir, addon_id, version):
    zip_name = f"{addon_id}-{version}.zip"
    zip_path = os.path.join(target_dir, addon_id, zip_name)
    
    os.makedirs(os.path.join(target_dir, addon_id), exist_ok=True)
    
    print(f"Creating zip for {addon_id} v{version}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(addon_id, os.path.relpath(file_path, addon_dir))
                zipf.write(file_path, arcname)
                
    # Copy icon.png if exists
    icon_path = os.path.join(addon_dir, 'icon.png')
    if os.path.exists(icon_path):
        shutil.copy(icon_path, os.path.join(target_dir, addon_id, 'icon.png'))
        
    return zip_path

def generate_repo(base_path):
    docs_dir = os.path.join(base_path, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    addons = ['plugin.video.dynamic_mpd', 'repository.dynamic_mpd']
    addons_xml_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<addons>\n"
    
    for addon in addons:
        addon_dir = os.path.join(base_path, addon)
        addon_id, version = get_addon_info(addon_dir)
        if addon_id and version:
            create_zip(addon_dir, docs_dir, addon_id, version)
            
            # Append addon.xml content to addons.xml
            with open(os.path.join(addon_dir, 'addon.xml'), 'r', encoding='utf-8') as f:
                xml_content = f.read()
                # Remove <?xml...?>
                xml_content = xml_content.split('>', 1)[1]
                addons_xml_content += xml_content + "\n"
                
    addons_xml_content += "</addons>\n"
    
    addons_xml_path = os.path.join(docs_dir, 'addons.xml')
    with open(addons_xml_path, 'w', encoding='utf-8') as f:
        f.write(addons_xml_content)
        
    # Create md5
    m = hashlib.md5()
    m.update(addons_xml_content.encode('utf-8'))
    with open(addons_xml_path + '.md5', 'w') as f:
        f.write(m.hexdigest())
        
    print("Repository built successfully in docs/ folder!")

if __name__ == '__main__':
    generate_repo(os.path.dirname(os.path.abspath(__file__)))
