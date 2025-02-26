

import sqlite3

def delete_files_by_ids(db_path, ids_list):
    """
    Delete multiple rows from the 'files' table by their IDs.
    Pass a list of IDs, e.g. [1839, 1838, 1840].
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a string with the correct number of placeholders
    placeholders = ",".join("?" * len(ids_list))
    
    # Build the query using the placeholders
    query = f"DELETE FROM files WHERE id IN ({placeholders})"
    
    # Execute the query, passing in the IDs as parameters
    cursor.execute(query, ids_list)
    
    conn.commit()
    conn.close()


delete_files_by_ids("obsidian_index.db", [1843, 1844, 1845, 1846, 1847])