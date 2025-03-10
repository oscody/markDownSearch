from git import Repo
import os


def get_repo(repo_path):
    # Try to initialize the repo
    repo = Repo(repo_path)

    if not repo.git_dir:
        print(f"Not a valid git repository: {repo_path}")
        return None  

    return repo



def files_changed(repo_path):
    
    # Check if path exists
    if not os.path.exists(repo_path):
        print(f"Path does not exist: {repo_path}")
        return []
    
    try:
        # Try to initialize the repo
        repo = get_repo(repo_path)
        
        # Get unstaged changes
        changed_files = [item.a_path for item in repo.index.diff(None)]
        
        
        if not changed_files :
            print("No changes detected in the repository")
        else:
            print(f"Changed files: {changed_files}")
        
        return changed_files
    
    except Exception as e:
        print(f"Error accessing git repository: {e}")
        return []


def get_files_modified(repo_path):
    
    # Check if path exists
    if not os.path.exists(repo_path):
        print(f"Path does not exist: {repo_path}")
        return []
    
    try:
        repo = get_repo(repo_path)
        
        # Get all unstaged changes
        diff_items = repo.index.diff(None)
        
        # Identify unstaged deletions (files deleted from the working tree)
        deleted_files = [item.a_path for item in diff_items if item.change_type == 'D']
        if deleted_files:
            print(f"Removing deleted files from index: {deleted_files}")
            repo.index.remove(deleted_files)
        
        # For the remaining changed files (non-deletions)
        changed_files = [item.a_path for item in diff_items if item.change_type != 'D']
        
        if not changed_files :
            print("No changes detected in the repository")
        else:
            print(f"Changed files: {changed_files}")
        
        return changed_files
    
    except Exception as e:
        print(f"Error accessing git repository: {e}")
        return []


def files_added(repo_path):
    
    # Check if path exists
    if not os.path.exists(repo_path):
        print(f"Path does not exist: {repo_path}")
        return []
    
    try:
       
        repo = get_repo(repo_path)

        return repo.untracked_files
    
    except Exception as e:
        print(f"Error accessing git repository: {e}")
        return []




def  main():

    # get_files_modified
    changed_files = files_added("/Users/bogle/Dev/obsidian/Bogle/")
    print(f"Total files with changes: {changed_files}")
    print(f"Total files with changes: {len(changed_files)}")


if __name__ == '__main__':
    main()