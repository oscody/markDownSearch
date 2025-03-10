from git import Repo
import os
import datetime

def log_git_changes(repo_path, log_file_path='md_fileagent/git/git_file_changes.log'):
    """
    Log files that have been changed or added in a Git repository.
    
    Args:
        repo_path: Path to the Git repository
        log_file_path: Path to the log file
    """
    try:
        # Initialize repo
        repo = Repo(repo_path)
        
        # Check if it's a valid git repository
        if not repo.git_dir:
            print(f"Not a valid git repository: {repo_path}")
            return
        
        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get unstaged changes (modified files)
        modified_files = [item.a_path for item in repo.index.diff(None)]
        
        # # Get staged changes
        # staged_files = [item.a_path for item in repo.index.diff('HEAD')]
        
        # Get untracked files (new files)
        untracked_files = repo.untracked_files
        
        # Create log entry
        log_entry = f"--- {timestamp} ---\n"
        
        if modified_files:
            log_entry += "Modified files:\n"
            for file in modified_files:
                log_entry += f"  - {file}\n"
        
        # if staged_files:
        #     log_entry += "Staged files:\n"
        #     for file in staged_files:
        #         log_entry += f"  - {file}\n"
        
        if untracked_files:
            log_entry += "New files:\n"
            for file in untracked_files:
                log_entry += f"  - {file}\n"
        
        if not (modified_files or untracked_files):
            log_entry += "No changes detected\n"
        
        log_entry += "\n"
        
        # Write to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)
        
        print(f"Changes logged to {log_file_path}")
        return modified_files , untracked_files
    
    except Exception as e:
        error_message = f"Error logging changes: {e}\n"
        print(error_message)
        
        # Log the error
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"--- {timestamp} ---\n")
            log_file.write(error_message)
            log_file.write("\n")
        
        return [], [], []

# Example usage:
if __name__ == "__main__":
    # Adjust this path to your repository
    # repo_path = "/Users/bogle/Dev/obsidian/Bogle/"
    # modified, new = log_git_changes(repo_path)


    base_dir = os.getcwd()

    print(f"files: {base_dir}")
    
    # print(f"Modified files: {len(modified)}")
    # print(f"New files: {len(new)}")