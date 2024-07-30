import zipfile
import os
import shutil
from tqdm import tqdm
from datetime import datetime

def unzip_repository(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

def format_code(content, lang):
    return f"```{lang}\n{content}\n```"

def file_to_markdown(file_path):
    ext = os.path.splitext(file_path)[1][1:]  # Remove the dot for language
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        if ext in ['py', 'js', 'css', 'html']:  # Extend this list as needed
            return format_code(content, ext)
        elif ext == 'md':
            return content  # Preserve Markdown formatting
        else:
            # For non-code text files, consider simple text formatting
            return content
    except UnicodeDecodeError:
        return f"Unable to display content for {file_path}. Binary or unsupported text encoding."

def create_markdown_document(startpath, output_md_file):
    with open(output_md_file, 'w', encoding='utf-8') as md_file:
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            if level == 0:
                header = '#' * 1 + ' ' + os.path.basename(root)
            else:
                header = '#' * (level + 1) + ' ' + os.path.basename(root)
            md_file.write(f"{header}\n\n")
            for f in sorted(files):
                file_path = os.path.join(root, f)
                md_file.write(f"## {f}\n\n")
                md_file.write(f"{file_to_markdown(file_path)}\n\n")
            md_file.write(f"```\n")

def get_latest_modified_date(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        info_list = zip_ref.infolist()
        latest_date = max(info.date_time for info in info_list)
    return datetime(*latest_date).strftime('%Y%m%d_%H%M%S')

def main():
    # Find all zip files in the same directory as the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    zip_files = [f for f in os.listdir(current_dir) if f.endswith('.zip')]

    for zip_filename in zip_files:
        base_name = os.path.splitext(zip_filename)[0]
        zip_path = os.path.join(current_dir, zip_filename)

        # Get the latest modified date and time from the zip file
        latest_modified = get_latest_modified_date(zip_path)
        folder_name = f"{base_name}_{latest_modified}"

        # Create the project folder
        project_folder = os.path.join(current_dir, folder_name)
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)

        # Move the zip file into the project folder
        shutil.move(zip_path, os.path.join(project_folder, zip_filename))

        # Unzip the repository
        extract_path = os.path.join(project_folder, 'extracted')
        unzip_repository(os.path.join(project_folder, zip_filename), extract_path)

        # Count the number of files for the progress bar
        file_count = sum(len(files) for _, _, files in os.walk(extract_path))

        # Create the Markdown document
        output_md_file = os.path.join(project_folder, f'{base_name}_overview.md')
        with tqdm(total=file_count, desc=f"Processing {zip_filename}") as pbar:
            with open(output_md_file, 'w', encoding='utf-8') as md_file:
                for root, dirs, files in os.walk(extract_path):
                    level = root.replace(extract_path, '').count(os.sep)
                    if level == 0:
                        header = '#' * 1 + ' ' + os.path.basename(root)
                    else:
                        header = '#' * (level + 1) + ' ' + os.path.basename(root)
                    md_file.write(f"{header}\n\n")
                    for f in sorted(files):
                        file_path = os.path.join(root, f)
                        md_file.write(f"## {f}\n\n")
                        md_file.write(f"{file_to_markdown(file_path)}\n\n")
                    md_file.write(f"```\n")
                    pbar.update(len(files))

if __name__ == "__main__":
    main()
