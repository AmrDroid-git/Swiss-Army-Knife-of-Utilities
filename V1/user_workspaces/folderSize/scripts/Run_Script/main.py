import os
import sys

def format_size(size_in_bytes):
    """
    Converts a size in bytes to a human-readable format (KB, MB, GB, etc.).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def calculate_folder_size(folder_path):
    """
    Recursively calculates the total size of all files in a given folder.
    """
    total_size = 0

    # os.walk automatically goes through the main folder and all subfolders
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            # Create the full, absolute path to the file
            filepath = os.path.join(dirpath, filename)
            
            # We skip symbolic links (shortcuts) to avoid counting the same file twice
            # or getting trapped in an infinite loop
            if not os.path.islink(filepath):
                # Get the size of the file in bytes and add it to the total
                total_size += os.path.getsize(filepath)

    return total_size

# --- Run the Script ---
if __name__ == "__main__":
    folder_input = sys.argv[1]

    # Verify that the path actually exists and is a directory
    if os.path.isdir(folder_input):
        print(f"\nScanning '{folder_input}'...")
        raw_size = calculate_folder_size(folder_input)
        readable_size = format_size(raw_size)
        
        print(f"Total size in bytes: {raw_size}")
        print(f"Human-readable size: {readable_size}")
    else:
        print("\nError: The path provided is not a valid folder. Please check your spelling and try again.")