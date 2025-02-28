import os
import re
from pathlib import Path
import yaml

def extract_tags_from_file(file_path):
    """Extract tags from only the 'tags:' field in a markdown file's frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract the YAML frontmatter between --- markers
    frontmatter_match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL)
    if not frontmatter_match:
        return set()
    
    frontmatter_text = frontmatter_match.group(1)
    
    try:
        # Parse the YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_text)
        
        # Extract tags from only the 'tags' field
        tags = frontmatter.get('tags', [])
        
        # Handle different formats of tags (string, list, etc.)
        if isinstance(tags, str):
            # Split comma-separated tags if it's a string
            tags = [tag.strip() for tag in tags.split(',')]
        elif isinstance(tags, list):
            # Keep as is if it's already a list
            pass
        else:
            # Return empty set for other cases
            return set()
        
        # Convert to set to remove duplicates and normalize
        return {tag.strip() for tag in tags if tag and tag.strip()}
    
    except yaml.YAMLError:
        # Return empty set if there's an error parsing the YAML
        return set()

def read_existing_tag_list(tag_list_file):
    """Read existing tags from a markdown file with #tag format."""
    existing_tags = set()
    
    if os.path.exists(tag_list_file):
        with open(tag_list_file, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Find all #tag patterns in the content
        # The pattern looks for # followed by letters, numbers, hyphens, and underscores
        tag_pattern = r'#([a-zA-Z0-9_-]+)'
        matches = re.findall(tag_pattern, content)
        
        # Add all found tags to the set
        existing_tags.update(matches)
    
    return existing_tags

def update_tag_list_file(tag_list_file, all_tags):
    """Update the markdown tag list file with new tags."""
    # Sort tags alphabetically for better readability
    sorted_tags = sorted(all_tags)
    
    # Format tags with # prefix, one per line
    formatted_tags = [f"#{tag}" for tag in sorted_tags]
    content = "\n".join(formatted_tags)
    
    # Write to the file
    with open(tag_list_file, 'w', encoding='utf-8') as file:
        file.write(content)

def process_markdown_files(markdown_dir, tag_list_file):
    """Process all markdown files in directory and update tag list."""
    all_extracted_tags = set()
    processed_files = 0
    markdown_files = list(Path(markdown_dir).glob('**/*.md'))
    
    # Skip the tag list file itself if it's in the markdown directory
    tag_list_path = Path(tag_list_file).resolve()
    
    for file_path in markdown_files:
        if file_path.resolve() == tag_list_path:
            continue
            
        tags = extract_tags_from_file(file_path)
        all_extracted_tags.update(tags)
        processed_files += 1
    
    # Read existing tags
    existing_tags = read_existing_tag_list(tag_list_file)
    
    # Find new tags that don't exist in the current list
    new_tags = all_extracted_tags - existing_tags
    
    # Update the tag list with all tags (existing + new)
    if new_tags:
        all_tags = existing_tags.union(all_extracted_tags)
        update_tag_list_file(tag_list_file, all_tags)
    
    return new_tags, processed_files

if __name__ == "__main__":
    # Configure these paths for your environment
    markdown_directory = "/Users/bogle/Dev/obsidian/Bogle"
    tag_list_file = "/Users/bogle/Dev/Agent/markDownSearch/md_fileagent/tags_list.md"
    
    new_tags, processed_files = process_markdown_files(markdown_directory, tag_list_file)
    
    print(f"Processed {processed_files} markdown files.")
    if new_tags:
        print(f"Added {len(new_tags)} new tags: {', '.join(sorted(new_tags))}")
    else:
        print("No new tags found.")