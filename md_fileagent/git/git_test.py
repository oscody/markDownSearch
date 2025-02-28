from git import Repo
import os

def get_changed_files(repo_path='/Users/bogle/Dev/obsidian/Bogle/'):
    # Check if path exists
    if not os.path.exists(repo_path):
        print(f"Path does not exist: {repo_path}")
        return []
    
    try:
        # Try to initialize the repo
        repo = Repo(repo_path)
        
        # Check if it's actually a git repository
        if not repo.git_dir:
            print(f"Not a valid git repository: {repo_path}")
            return []
        
        # Get unstaged changes
        changed_files = [item.a_path for item in repo.index.diff(None)]
        
        # Get staged changes
        staged_files = [item.a_path for item in repo.index.diff('HEAD')]
        
        if not changed_files and not staged_files:
            print("No changes detected in the repository")
        else:
            print(f"Changed files: {changed_files}")
            print(f"Staged files: {staged_files}")
        
        return changed_files + staged_files
    
    except Exception as e:
        print(f"Error accessing git repository: {e}")
        return []

# Call the function
changed_files = get_changed_files()
print(f"Total files with changes: {len(changed_files)}")