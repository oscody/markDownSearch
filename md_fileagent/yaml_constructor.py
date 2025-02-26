import re
import yaml

def has_frontmatter(content):
    """Check if the content contains a YAML frontmatter block."""
    return bool(re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL))


def update_frontmatter(content , ai_suggestd_old, ai_suggestd_new, writerName , time):

    # Extract YAML frontmatter (assumes it’s the first block in the file)
    frontmatter_match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    
    if frontmatter_match:
        yaml_text = frontmatter_match.group(1)
        data = yaml.safe_load(yaml_text) or {}
    else:
        # If no frontmatter exists, create an empty dict
        data = {}

    # Update or add the new keys
    data['ai-suggestd-old'] = ai_suggestd_old
    data['ai-suggestd-new'] = ai_suggestd_new
    data['script-writer'] = writerName
    data['script-run-date'] = time

    # Dump the updated YAML block back to a string
    new_yaml_block = '---\n' + yaml.dump(data, sort_keys=False) + '---\n\n'
    
    # Replace the old YAML block with the new one (or prepend if none was found)
    if frontmatter_match:
        updated_content = re.sub(r'^---\n(.*?)\n---\n', new_yaml_block, content, count=1, flags=re.DOTALL)
    else:
        updated_content = new_yaml_block + content

    return updated_content

def create_frontmatter(filename, creation_date_str, writerName, script_run_time_str, content):
        return (
        "---\n"
        f"name: {filename}\n"
        f"tags: \n"
        f"date-created: {creation_date_str}\n"
        f"script-writer: {writerName}\n"
        f"script-run-date: {script_run_time_str}\n"
        "---\n\n"
        f"{content}\n"
    )
