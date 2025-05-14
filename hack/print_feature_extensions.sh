#!/usr/bin/env bash


search_and_print_directories() {
    local pattern="$1"
    local base_pattern="${pattern%%.*}" 
    
    while IFS= read -r file; do
        dir=$(dirname "$file" | sed 's|^\./||')
        
        suffix="${file##*/}"
        suffix="${suffix#"$base_pattern"}" 
        
        echo "('$dir', '$suffix'),"
    done < <(find . -type f -name "$pattern" | sort -u)
}


echo "All features with a non-default image archive filetype:"
search_and_print_directories "image.*"

echo "All features with a non-default image filetype:"
search_and_print_directories "convert.*"
