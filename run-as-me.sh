#!/bin/bash

# Username to run the script as
USERNAME="ricardo"

# Log file
LOG_FILE="/home/$USERNAME/scripts/desliga.log"

# Set the XDG_RUNTIME_DIR environment variable
export XDG_RUNTIME_DIR="/run/user/$(id -u $USERNAME)"
echo "XDG_RUNTIME_DIR set to $XDG_RUNTIME_DIR" >> $LOG_FILE

# Ensure the .Xauthority file is correctly pointed to
XAUTH_FILE="/home/$USERNAME/.Xauthority"
if [ -f "$XAUTH_FILE" ]; then
    export XAUTHORITY=$XAUTH_FILE
    echo ".Xauthority file found and set" >> $LOG_FILE
else
    echo ".Xauthority file not found at $XAUTH_FILE" >> $LOG_FILE
fi

# Change directory to the location of your Python script
cd /home/$USERNAME/scripts
echo "Changed directory to /home/$USERNAME/scripts" >> $LOG_FILE

# Array of DISPLAY values to try
displays=(":1" ":0" ":2")

# Loop through each DISPLAY value
for display in "${displays[@]}"
do
    echo "Trying with DISPLAY=$display" >> $LOG_FILE
    export DISPLAY=$display

    # Run the Python script as the specified user
    if sudo -u $USERNAME /usr/bin/python3 desliga.py >> $LOG_FILE 2>&1; then
        echo "Script succeeded on DISPLAY=$display" >> $LOG_FILE
        break
    else
        echo "Script failed on DISPLAY=$display, trying next one..." >> $LOG_FILE
    fi
done