#!/bin/bash

# Define where to store the log file
LOG_FILE="/var/log/sys_usage.log"

# Create log file if it doesn't exist
touch $LOG_FILE

while true; do
    # Get current timestamp
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Extract CPU usage using top command (summing user and system usage)
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    
    # Calculate Memory usage (used/total * 100)
    MEM_USAGE=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
    
    # Append the data to the log file
    echo "$TIMESTAMP, CPU: $CPU_USAGE%, Memory: $MEM_USAGE%" >> $LOG_FILE
    
    # Wait for 5 seconds before next sample
    sleep 5
done

