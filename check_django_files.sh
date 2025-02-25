#!/bin/bash

# List of directories to check (modify as needed)
DIRECTORIES=("communications" "dashboard" "profiles" "projects" "users")

# List of required files in each directory
REQUIRED_FILES=("models.py" "views.py" "serializers.py" "urls.py" "permissions.py")

# Loop through each directory in the list
for dir in "${DIRECTORIES[@]}"; do
    # Check if the directory exists
    if [ -d "$dir" ]; then
        echo "Checking directory: $dir"
        
        # Loop through required files
        for file in "${REQUIRED_FILES[@]}"; do
            if [ ! -f "$dir/$file" ]; then
                echo "Creating missing file: $dir/$file"
                touch "$dir/$file"
            fi
        done
    else
        echo "Directory not found: $dir"
    fi
done

echo "Check completed!"
