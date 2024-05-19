# !/bin/bash

# Files to update
FILE="/usr/local/lib/python3.11/site-packages/basicsr/data/degradations.py"

# update line 8 
OLD_LINE_8="from torchvision.transforms.functional_tensor import rgb_to_grayscale"
NEW_LINE_8="# from torchvision.transforms.functional_tensor import rgb_to_grayscale"

# Update line matching OLD_LINE_8 with NEW_LINE_8 in the file
sed -i "s|$OLD_LINE_8|$NEW_LINE_8|" "$FILE"
