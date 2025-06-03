#!/bin/bash

for file in *; do
  # Make sure it’s a reg file 
  if [ -f "$file" ]; then
    # Print even lines with line numbers
    awk 'NR % 2 == 0 { print FILENAME ": " $0 }' "$file"
  fi
done
