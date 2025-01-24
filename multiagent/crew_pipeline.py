# crew_pipeline.py

import os
from note_preprocessor import NotePreprocessorAgent
from hashtag_generator import HashtagGeneratorAgent
from link_extractor import LinkExtractorAgent
from link_content_analyzer import LinkContentAnalyzerAgent
from aggregator import AggregatorAgent
import ollama

# Specify the AI model to use
model_name = "llama3.2"

ollama_client = ollama.Client()

class CrewPipeline:
    def __init__(self):
        self.note_preprocessor = NotePreprocessorAgent()
        self.hashtag_generator = HashtagGeneratorAgent(ollama_client,model_name)
        self.link_extractor = LinkExtractorAgent()
        self.link_analyzer = LinkContentAnalyzerAgent(ollama_client,model_name)
        self.aggregator = AggregatorAgent(ollama_client,model_name)

    def process_note(self, note: str) -> dict:
        """
        Runs a single note through the multi-agent pipeline.
        """
        # Step 1: Preprocess
        preproc_result = self.note_preprocessor.run(note)
        cleaned_note = preproc_result["cleaned_note"]
        links = preproc_result["links"]

        # Step 2: If no links, just generate hashtags from note content
        if not links:
            note_tags = self.hashtag_generator.run(cleaned_note)
            final_tags = self.aggregator.run(note_tags, [])
            return {
                "original_note": note,
                "cleaned_note": cleaned_note,
                "hashtags": final_tags
            }

        # Step 3: If there are links, extract valid links
        link_extraction_result = self.link_extractor.run(links)
        valid_links = link_extraction_result["valid_links"]

        # Step 4: Analyze link content and generate link-based hashtags
        link_analysis_result = self.link_analyzer.run(valid_links)
        link_based_hashtags = link_analysis_result["link_based_hashtags"]

        # Step 5: Generate hashtags for the note content itself
        note_tags = self.hashtag_generator.run(cleaned_note)

        # Step 6: Combine everything in the Aggregator
        final_tags = self.aggregator.run(note_tags, link_based_hashtags)

        return {
            "valid_links": valid_links,
            "link_analysis": link_analysis_result["link_analysis"],
            "hashtags": final_tags
        }



def process_markdown_files(input_dir, allowed_dirs=None, file_limit=None, specific_file=None):
    """
    Process markdown files from a given directory with flexible options.
    
    :param input_dir: Root directory to search for markdown files
    :param allowed_dirs: Set of subdirectories to search within (optional)
    :param file_limit: Maximum number of files to process (optional)
    :param specific_file: Full path to a specific file to process (optional)
    """
    file_count = 0
    processed_files = []

    # If a specific file is provided, process only that file
    if specific_file:
        if specific_file.lower().endswith('.md'):
            try:
                with open(specific_file, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                    processed_files.append({
                        'path': specific_file,
                        'content': content
                    })
                return processed_files
            except Exception as e:
                print(f"Error processing specific file {specific_file}: {e}")
                return []

    # Walk through directory
    for root, dirs, files in os.walk(input_dir):
        # Filter directories if allowed_dirs is specified
        if allowed_dirs:
            dirs[:] = [d for d in dirs if d in allowed_dirs]

        for filename in files:
            # Skip non-markdown files
            if not filename.lower().endswith('.md'):
                continue

            # Construct full file path
            file_path = os.path.join(root, filename)

            # Process file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                    processed_files.append({
                        'path': file_path,
                        'content': content
                    })

                    # Increment file count
                    file_count += 1

                    # Break if file limit is reached
                    if file_limit is not None and file_count >= file_limit:
                        break

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

            # Break outer loop if file limit is reached
            if file_limit is not None and file_count >= file_limit:
                break

        # Break if file limit is reached
        if file_limit is not None and file_count >= file_limit:
            break

    return processed_files

if __name__ == "__main__":
    pipeline = CrewPipeline()

    input_dir = '/Users/bogle/Dev/obsidian/Bogle'
    allowed_dirs = {"1. Projects", "2. Areas", "3. Resources", "4. Archives"}
    
    # # Option 1: Process with file limit
    # processed_files = process_markdown_files(
    #     input_dir, 
    #     allowed_dirs=allowed_dirs, 
    #     file_limit=1  # Limit to 1 file
    # )

    # 2: Process a specific file
    # specific_file = '/Users/bogle/Dev/obsidian/Bogle/4. Archives/Evernote/nians notebook/Wix Support wayne.md'
    # specific_file = '/Users/bogle/Dev/obsidian/Bogle/4. Archives/Evernote/nians notebook/vpn.md'
    specific_file = '/Users/bogle/Dev/obsidian/Bogle/2. Areas/multiagent tester.md'
    specific_files = process_markdown_files(
        input_dir, 
        specific_file=specific_file
    )

    results = []

    for file_info in specific_files:
        print(f"Processed File: {file_info['path']}")
        print(f"Content Length: {file_info['content']} characters")
        print("---")


        result = pipeline.process_note(file_info['content'])
        results.append(result)

        # Print or store the final results
        for idx, res in enumerate(results, start=1):
            if "valid_links" in res:
                print("Valid Links:", res["valid_links"])
            print("Hashtags:", res["hashtags"])
            print()