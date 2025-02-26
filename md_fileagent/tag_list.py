


import re

def tag_list():
    # Read the markdown file containing tags
    with open("/Users/bogle/Dev/Agent/markDownSearch/md_fileagent/tags_list.md", "r") as f:
        md_content = f.read()

    # Extract tags that start with '#'
    # This regex finds any non‑whitespace characters following a '#'
    tags = re.findall(r"#\S+", md_content)

    # remove duplicates and sort them
    tags = sorted(set(tags))

    existing_tags_line = "Consider existing tags: " + ", ".join(tags)

    return existing_tags_line
    

import re

def tag_cleaner(tag_dict_or_model):
    # If it's a Pydantic model, convert to a dict
    if hasattr(tag_dict_or_model, 'dict') and callable(tag_dict_or_model.dict):
        data = tag_dict_or_model.dict()
    # Otherwise, if it's a custom object, use vars()
    elif hasattr(tag_dict_or_model, '__dict__'):
        data = vars(tag_dict_or_model)
    else:
        # Assume it's already a dictionary
        data = tag_dict_or_model
    
    cleaned_dict = {}
    for key, tag in data.items():
        tag_str = str(tag)
        normalized = re.sub(r'[\s-]+', '', tag_str)
        if not normalized.startswith('#'):
            normalized = '#' + normalized
        cleaned_dict[key] = normalized
    return cleaned_dict


def tag_cleanerv2(tag_dict_or_model):
    # Convert to dict if necessary
    if hasattr(tag_dict_or_model, 'dict') and callable(tag_dict_or_model.dict):
        data = tag_dict_or_model.dict()
    elif hasattr(tag_dict_or_model, '__dict__'):
        data = vars(tag_dict_or_model)
    else:
        data = tag_dict_or_model

    cleaned_tags = []
    for key, tag in data.items():
        # Convert the tag to a string and strip extra whitespace
        tag_str = str(tag).strip()
        # Remove spaces and dashes if desired (this step can be adjusted)
        normalized = re.sub(r'[\s-]+', '', tag_str)
        # Remove any leading '#' characters
        normalized = normalized.lstrip('#')
        cleaned_tags.append(normalized)
        
    # Join the cleaned tags with comma separation
    return " , ".join(cleaned_tags)