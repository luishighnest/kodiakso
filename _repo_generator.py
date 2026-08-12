import os
import hashlib
import zipfile
import shutil
import xml.etree.ElementTree as ET

class Generator:
    """
    Generates a new addons.xml file from each addons addon.xml file
    and a md5 hash of new addons.xml file
    """
    def __init__(self):
        # Percorso della cartella contenente gli addon
        self.addons_dir = os.path.dirname(os.path.abspath(__file__))
        self.zips_dir = os.path.join(self.addons_dir, 'zips')

    def generate(self):
        # 1. Crea file zip
        self._create_zips()
        
        # 2. Genera addons.xml e md5
        print("Generating addons.xml...")
        addons_xml_path = os.path.join(self.addons_dir, "addons.xml")
        md5_path = os.path.join(self.addons_dir, "addons.xml.md5")

        try:
            self._generate_addons_file(addons_xml_path)
            self._generate_md5_file(addons_xml_path, md5_path)
            print("Successfully generated addons.xml and addons.xml.md5")
        except Exception as e:
            print(f"Error generating repository files: {e}")

    def _create_zips(self):
        print("Creating zip files...")
        if not os.path.exists(self.zips_dir):
            os.makedirs(self.zips_dir)

        # Trova tutte le cartelle degli addon
        for addon_id in os.listdir(self.addons_dir):
            addon_path = os.path.join(self.addons_dir, addon_id)
            addon_xml_path = os.path.join(addon_path, "addon.xml")
            
            # Salta se non è un addon o è la cartella zips
            if not os.path.isdir(addon_path) or addon_id == "zips" or not os.path.exists(addon_xml_path):
                continue

            try:
                tree = ET.parse(addon_xml_path)
                root = tree.getroot()
                version = root.get('version')
                
                # Crea la cartella per lo zip dell'addon specifico
                addon_zip_dir = os.path.join(self.zips_dir, addon_id)
                if not os.path.exists(addon_zip_dir):
                    os.makedirs(addon_zip_dir)
                    
                zip_name = f"{addon_id}-{version}.zip"
                zip_path = os.path.join(addon_zip_dir, zip_name)
                
                print(f"Zipping {addon_id} v{version} to {zip_path}")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root_dir, dirs, files in os.walk(addon_path):
                        for file in files:
                            file_path = os.path.join(root_dir, file)
                            arcname = os.path.join(addon_id, os.path.relpath(file_path, addon_path))
                            zipf.write(file_path, arcname)
                            
            except Exception as e:
                print(f"Error zipping {addon_id}: {e}")


    def _generate_addons_file(self, addons_xml_path):
        addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
        
        for addon_id in os.listdir(self.addons_dir):
            addon_path = os.path.join(self.addons_dir, addon_id)
            addon_xml_path = os.path.join(addon_path, "addon.xml")
            
            if os.path.isdir(addon_path) and addon_id != "zips" and os.path.exists(addon_xml_path):
                try:
                    with open(addon_xml_path, "r", encoding="utf-8") as f:
                        xml_content = f.read()
                        
                    # Rimuovi intestazione xml dal file originale
                    xml_content = xml_content.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')
                    addons_xml += xml_content.strip() + "\n\n"
                except Exception as e:
                    print(f"Error reading addon.xml for {addon_id}: {e}")

        addons_xml += "</addons>\n"
        
        with open(addons_xml_path, "w", encoding="utf-8") as f:
            f.write(addons_xml)

    def _generate_md5_file(self, addons_xml_path, md5_path):
        try:
            with open(addons_xml_path, "rb") as f:
                content = f.read()
            m = hashlib.md5(content).hexdigest()
            with open(md5_path, "w", encoding="utf-8") as f:
                f.write(m)
        except Exception as e:
            print(f"Error creating MD5 file: {e}")

if __name__ == "__main__":
    Generator().generate()
