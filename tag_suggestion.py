import os
import sqlite3
import logging
from datetime import datetime


from ai_service import OllamaService , OpenAIService
from md_fileagent.tag_prompt import tag_prompt , tag_prompt_oldtags , new_tag_prompt , new_tag_promptv2
from md_fileagent.tag_list import tag_list , tag_cleaner , tag_cleanerv2
from md_fileagent.tag_sqlite import check_for_ai_suggestions , add_file_with_tags , initialize_db , add_file , select_all_db , update_file_with_tags
from md_fileagent.yaml_constructor import update_frontmatter, create_frontmatter , has_frontmatter
from md_fileagent.utility import get_date_time
from md_fileagent.file_writer import update_file , get_file_content, get_all_files, get_filename , get_file_path
from md_fileagent.git_helper import files_added , files_changed , get_files_modified
from md_fileagent.tag_daemonv2 import start_process
from pydantic import BaseModel

class TagModel(BaseModel):
    tag1: str
    tag2: str
    tag3: str

# Set up logging to file.
logging.basicConfig(
    filename='app.log',          # Log file name
    filemode='a',                # Append mode (use 'w' to overwrite)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO           # Minimum log level to capture
)

def get_new_files(db_path, directory):
    """
    Returns a list of full file paths for Markdown files in the directory 
    that are not already in the database.
    """

    all_files = get_all_files(directory)
    
    existing_files = select_all_db(db_path)
    
    # Only consider files in allowed directories
    allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}

    new_files = [
        f for f in (all_files - existing_files)
        if os.path.relpath(f, directory).split(os.sep)[0] in allowed_dirs
    ]
    return new_files


def prepare_files(file_path):
    
    file_path = get_file_path(file_path)

    # Extract the file name from the full file path
    file_name = get_filename(file_path)
    
    # New file: read content and insert a new record.
    content = get_file_content(file_path)
    
    # Generate metadata using tag_prompt and the tagging service.
    existing_tags = tag_list()

    return file_path , file_name , content , existing_tags


def process_file_newfiles(file_path):

    file_path = get_file_path(file_path)
    # Extract the file name from the full file path
    file_name = get_filename(file_path)
    
    # New file: read content and insert a new record.
    content = get_file_content(file_path)
    
    # Generate metadata using tag_prompt and the tagging service.
    existing_tags = tag_list()

    prompt = tag_prompt([file_name], [content], existing_tags, 3)
    old_prompt= tag_prompt_oldtags([file_name], [content], existing_tags, 3)
    new_prompt = new_tag_prompt([file_name], [content] , 3)
    new_promptv2 = new_tag_promptv2([file_name], [content] , 3)

    metadata_info = OllamaService(prompt, TagModel)
    old_metadata_info = OllamaService(old_prompt, TagModel)
    new_metadata_info = OllamaService(new_prompt, TagModel)
    new_metadata_infov2 = OllamaService(new_promptv2, TagModel)
    # metadata_info = OpenAIService(prompt, TagModel)


    cleantags = tag_cleanerv2(metadata_info)
    cleantagsv2 = tag_cleanerv2(old_metadata_info)
    clean_new_metadata_info = tag_cleanerv2(new_metadata_info)
    clean_new_metadata_infov2 = tag_cleanerv2(new_metadata_infov2)


    logging.info(f"Processed new file {file_path} with metadata: {cleantags}")
    # print(f"Processed new file {file_path} with metadata: {cleantags}")

    logging.info(f"Processed new file {file_path} with metadata: {cleantagsv2}")
    print(f"Processed new file {file_path} with metadata: {cleantagsv2}")

    logging.info(f"Processed new file {file_path} with new metadata: {clean_new_metadata_info}")
    print(f"Processed new file {file_path} with metadata: {clean_new_metadata_info}")

    logging.info(f"Processed new file {file_path} with new metadata V2: {clean_new_metadata_infov2}")
    # print(f"Processed new file {file_path} with metadata: {clean_new_metadata_infov2}")

    time = get_date_time()
    if not has_frontmatter(content):

        content = create_frontmatter(file_name,time , 'tagwriter' , time, content)

    updated_tag = update_frontmatter(content,cleantagsv2 , clean_new_metadata_infov2 , 'tagwriter' , time)
    update_file(file_path , updated_tag)

    # add_file_with_tags(file_path, cleantagsv2, clean_new_metadata_infov2 , time)



def process_file_changed(file_path):


    file_path , file_name , content , existing_tags = prepare_files(file_path)

    prompt = tag_prompt([file_name], [content], existing_tags, 3)
    old_prompt= tag_prompt_oldtags([file_name], [content], existing_tags, 3)
    new_prompt = new_tag_prompt([file_name], [content] , 3)
    new_promptv2 = new_tag_promptv2([file_name], [content] , 3)

    metadata_info = OllamaService(prompt, TagModel)
    old_metadata_info = OllamaService(old_prompt, TagModel)
    new_metadata_info = OllamaService(new_prompt, TagModel)
    new_metadata_infov2 = OllamaService(new_promptv2, TagModel)
    # metadata_info = OpenAIService(prompt, TagModel)


    cleantags = tag_cleanerv2(metadata_info)
    cleantagsv2 = tag_cleanerv2(old_metadata_info)
    clean_new_metadata_info = tag_cleanerv2(new_metadata_info)
    clean_new_metadata_infov2 = tag_cleanerv2(new_metadata_infov2)


    logging.info(f"Processed new file {file_path} with metadata: {cleantags}")
    # print(f"Processed new file {file_path} with metadata: {cleantags}")

    logging.info(f"Processed new file {file_path} with metadata: {cleantagsv2}")
    print(f"Processed new file {file_path} with metadata: {cleantagsv2}")

    logging.info(f"Processed new file {file_path} with new metadata: {clean_new_metadata_info}")
    print(f"Processed new file {file_path} with metadata: {clean_new_metadata_info}")

    logging.info(f"Processed new file {file_path} with new metadata V2: {clean_new_metadata_infov2}")
    # print(f"Processed new file {file_path} with metadata: {clean_new_metadata_infov2}")

    time = get_date_time()
    if not has_frontmatter(content):

        content = create_frontmatter(file_name,time , 'tagwriter' , time, content)

    updated_tag = update_frontmatter(content,cleantagsv2 , clean_new_metadata_infov2 , 'tagwriter' , time)
    update_file(file_path , updated_tag)

    # update_file_with_tags(file_path, cleantagsv2, clean_new_metadata_infov2 , time)


def main():
    db_path = "obsidian_index.db"
    directory_to_scan = "/Users/bogle/Dev/obsidian/Bogle"
    # conn = initialize_db(db_path)
    
    # check_for_ai_suggestions(db_path)
    # Get list of new Markdown files
    # new_files = get_new_files(db_path, directory_to_scan)


    #checks for any new tags and updates list
    start_process()

    new_files = files_added(directory_to_scan)

    # Process each new file individually.
    for file_path in new_files:
        process_file_newfiles(file_path)

    changed_files = get_files_modified(directory_to_scan)
    
        # Process each new file individually.
    for file_path in changed_files:
        process_file_changed(file_path)

    
    print("End")
    # conn.close()

if __name__ == '__main__':
    main()