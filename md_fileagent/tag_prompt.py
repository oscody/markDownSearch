import tiktoken


def count_tokens(text, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

def tag_prompt(fileName, content, existing_tags_line, count):
    MAX_CONTEXT_LENGTH = 2048
    DESIRED_COMPLETION_TOKENS = 150

    # Function to count tokens using tiktoken
    def count_tokens(text, model="cl100k_base"):
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))

    prompt_template = """
    You are a precise tag generator. Analyze the content and suggest {count} relevant tags.
    {existing_tags_line}

    Guidelines:
    - must be a single continuous word or phrase with no internal spaces.
    - Prefer existing tags when appropriate (score them higher)
    - Create specific, meaningful new tags when needed
    - Score based on relevance (0-100)
    - Include brief reasoning for each tag
    - Focus on key themes, topics, and document type

    File: "{fileName}"
    Content:
    {content}
    """

    # Construct the initial prompt with all named parameters.
    prompt = prompt_template.format(
        fileName=fileName,
        content=content,
        existing_tags_line=existing_tags_line,
        count=count
    )

    # Count tokens in the prompt.
    prompt_tokens = count_tokens(prompt)

    # Truncate content if the combined token count exceeds the maximum context length.
    while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
        truncate_length = int(len(content) * 0.9)
        content = content[:truncate_length]
        prompt = prompt_template.format(
            fileName=fileName,
            content=content,
            existing_tags_line=existing_tags_line,
            count=count
        )
        prompt_tokens = count_tokens(prompt)

    return prompt

def tag_prompt_oldtags(fileName, content, existing_tags_line, count):
    MAX_CONTEXT_LENGTH = 2048
    DESIRED_COMPLETION_TOKENS = 150

    prompt_template = """
    Given the file "{fileName}" with the following content:
    \"\"\"
    {content}
    \"\"\"

    Select up to {count} tags **only from the following list** :
    Do not invent any new tags or modify the given tags.
    The tags you choose must match exactly (including case and punctuation) the ones provided in the list:
    {existing_tags_line}

    If none of these tags have an evident link to the main topics, return null.

    Return your answer strictly as JSON.
    """

    # Construct the initial prompt with all named parameters.
    prompt = prompt_template.format(
        fileName=fileName,
        content=content,
        existing_tags_line=existing_tags_line,
        count=count
    )

    # Count tokens in the prompt.
    prompt_tokens = count_tokens(prompt)

    # Truncate content if the combined token count exceeds the maximum context length.
    while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
        truncate_length = int(len(content) * 0.9)
        content = content[:truncate_length]
        prompt = prompt_template.format(
            fileName=fileName,
            content=content,
            existing_tags_line=existing_tags_line,
            count=count
        )
        prompt_tokens = count_tokens(prompt)

    return prompt

def new_tag_prompt(fileName, content, count):
    MAX_CONTEXT_LENGTH = 2048
    DESIRED_COMPLETION_TOKENS = 150

    prompt_template = """
    Analyze the content and suggest {count} relevant tags.

    Guidelines:
    - must be a single continuous word or phrase with no internal spaces.
    - Create specific, meaningful new tags when needed
    - Focus on key themes, topics, and document type

    File: "{fileName}"
    Content:
    {content}
    """

    # Construct the initial prompt with all named parameters.
    prompt = prompt_template.format(
        fileName=fileName,
        content=content,
        count=count
    )

    # Count tokens in the prompt.
    prompt_tokens = count_tokens(prompt)

    # Truncate content if the combined token count exceeds the maximum context length.
    while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
        truncate_length = int(len(content) * 0.9)
        content = content[:truncate_length]
        prompt = prompt_template.format(
            fileName=fileName,
            content=content,
            count=count
        )
        prompt_tokens = count_tokens(prompt)

    return prompt

def new_tag_promptv2(fileName, content, count):
    MAX_CONTEXT_LENGTH = 2048
    DESIRED_COMPLETION_TOKENS = 150

    prompt_template = """
    Analyze the content and suggest {count} relevant tags.

    1. One tag reflecting the topic or platform
    2. One tag indicating the document type (e.g., meeting_notes, research, brainstorm, draft).
    3. One more specific tag inspired by the file name 
    4. Use hyphens for multi-word tags.
    5. Ensure tags are concise and reusable across notes.
    6. Return null if no tags can be generated.
    7. Do not suggest tags that are already present in the content.


    Examples:
    - Use moderately broad tags like fitnessPlan, not overly specific like monday_dumbells_20kg.
    - For "humility and leadership", use humility.`

    File: "{fileName}"
    Content:
    {content}
    """
    prompt = prompt_template.format(
        fileName=fileName,
        content=content,
        count=count
    )

    prompt_tokens = count_tokens(prompt)

    # Truncate content if the combined token count exceeds the maximum context length.
    while prompt_tokens + DESIRED_COMPLETION_TOKENS > MAX_CONTEXT_LENGTH:
        truncate_length = int(len(content) * 0.9)
        content = content[:truncate_length]
        prompt = prompt_template.format(
            fileName=fileName,
            content=content,
            count=count
        )
        prompt_tokens = count_tokens(prompt)

    return prompt