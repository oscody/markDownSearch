import os
import re
from pathlib import Path
import yaml

def extract_tags_from_file(file_path):
    """Extract tags from the 'tags:' field in a markdown file's frontmatter."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the YAML frontmatter between --- markers
        frontmatter_match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
        if not frontmatter_match:
            return set()
        
        frontmatter_text = frontmatter_match.group(1)
        
        # Parse the YAML frontmatter
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            
            # Check if frontmatter is a dictionary (proper YAML)
            if not isinstance(frontmatter, dict):
                return set()
            
            # Extract tags from the 'tags' field
            tags = frontmatter.get('tags', [])
            
            # Handle different formats of tags (string, list, etc.)
            parts = []
            if isinstance(tags, str):
                # First split on commas if present; otherwise split on whitespace
                if ',' in tags:
                    parts = [tag.strip() for tag in tags.split(',') if tag.strip()]
                else:
                    parts = [tag.strip() for tag in tags.split() if tag.strip()]
            elif isinstance(tags, list):
                for item in tags:
                    if isinstance(item, str):
                        if ',' in item:
                            parts.extend([tag.strip() for tag in item.split(',') if tag.strip()])
                        else:
                            parts.extend([tag.strip() for tag in item.split() if tag.strip()])
            else:
                return set()
            
            # Further split tokens that contain spaces so that "Agents AI readme" becomes three tags
            final_tags = set()
            for part in parts:
                if ' ' in part:
                    final_tags.update([tag for tag in part.split() if tag])
                else:
                    final_tags.add(part)
            
            return final_tags
            
        except yaml.YAMLError:
            return set()
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return set()

def read_existing_tag_list(tag_list_file):
    """Read existing tags from a markdown file with #tag format."""
    existing_tags = set()
    
    try:
        if os.path.exists(tag_list_file):
            with open(tag_list_file, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Find all hashtag patterns and their following words
            lines = content.split('\n')
            for line in lines:
                # Process each line to extract tags
                if line.startswith('#'):
                    # Remove the # and split by spaces to separate multiple tags on one line
                    line_without_hash = line[1:].strip()
                    # Split by spaces and handle potential multi-word tags
                    parts = re.findall(r'([A-Za-z0-9_-]+)', line_without_hash)
                    existing_tags.update(parts)
    except Exception as e:
        print(f"Error reading tag list file: {str(e)}")
    
    return existing_tags

def update_tag_list_file(tag_list_file, all_tags):
    """Update the markdown tag list file with new tags."""
    try:
        # Sort tags alphabetically for better readability
        sorted_tags = sorted(all_tags)
        
        # Format tags with # prefix, one tag per line
        formatted_tags = [f"#{tag}" for tag in sorted_tags]
        content = "\n".join(formatted_tags)
        
        # Write to the file
        with open(tag_list_file, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Successfully wrote {len(sorted_tags)} tags to {tag_list_file}")
    except Exception as e:
        print(f"Error updating tag list file: {str(e)}")

def process_markdown_files(markdown_dir, tag_list_file):
    """Process all markdown files in directory and update tag list."""
    all_extracted_tags = set()
    processed_files = 0
    skipped_files = 0
    
    try:
        markdown_files = list(Path(markdown_dir).glob('**/*.md'))
        
        # Skip the tag list file itself if it's in the markdown directory
        tag_list_path = Path(tag_list_file).resolve()
        
        for file_path in markdown_files:
            if file_path.resolve() == tag_list_path:
                continue
                
            tags = extract_tags_from_file(file_path)
            if tags:
                all_extracted_tags.update(tags)
                processed_files += 1
            else:
                skipped_files += 1
        
        # Read existing tags
        existing_tags = read_existing_tag_list(tag_list_file)
        
        # Find new tags that don't exist in the current list
        new_tags = all_extracted_tags - existing_tags
        
        # Update the tag list with all tags (existing + new)
        if new_tags or not os.path.exists(tag_list_file):
            all_tags = existing_tags.union(all_extracted_tags)
            update_tag_list_file(tag_list_file, all_tags)
        
        return new_tags, processed_files, skipped_files
    
    except Exception as e:
        print(f"Error processing markdown files: {str(e)}")
        return set(), 0, 0

if __name__ == "__main__":
    # Configure these paths for your environment
    markdown_directory = "/Users/bogle/Dev/obsidian/Bogle"
    tag_list_file = "/Users/bogle/Dev/Agent/markDownSearch/md_fileagent/tags_list.md"
    
    new_tags, processed_files, skipped_files = process_markdown_files(markdown_directory, tag_list_file)
    
    print(f"Processed {processed_files} markdown files with valid tags.")
    print(f"Skipped {skipped_files} files without valid tags.")
    
    if new_tags:
        print(f"Added {len(new_tags)} new tags: {', '.join(sorted(new_tags))}")
    else:
        print("No new tags found.")