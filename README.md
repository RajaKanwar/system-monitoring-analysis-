# CPU and Memory Monitoring on Remote EC2 Instance

## Overview
This project involves creating a system to monitor CPU and memory usage on an Ubuntu-based EC2 instance. The solution consists of:

1. A **Shell Script** to log CPU and memory usage.
2. **Ansible** to deploy the script on a remote EC2 instance.
3. **Python** to extract and analyze the collected data.

---

## Prerequisites
Before running the scripts, ensure you have the following installed:

- Ubuntu system (local & remote EC2 instance)
- Ansible
- Python (with pandas, paramiko)
- SSH access to EC2 instance

---

## Step 1: Shell Script for Monitoring (`monitor.sh`)
The `monitor.sh` script logs CPU and memory usage at 5-second intervals.

### Usage
```bash
chmod +x monitor.sh
nohup ./monitor.sh &
```

---

## Step 2: Deploy the Script using Ansible

### **Ansible Playbook (`deploy_script.yml`):**
```yaml
---
- name: Deploy Monitoring Script
  hosts: remote
  become: yes
  tasks:
    - name: Copy script to remote server
      copy:
        src: monitor.sh
        dest: /usr/local/bin/monitor.sh
        mode: '0755'

    - name: Create systemd service for script
      copy:
        dest: /etc/systemd/system/monitor.service
        content: |
          [Unit]
          Description=CPU & Memory Monitor
          After=network.target

          [Service]
          ExecStart=/usr/local/bin/monitor.sh
          Restart=always

          [Install]
          WantedBy=multi-user.target

    - name: Reload systemd and enable service
      shell: |
        systemctl daemon-reload
        systemctl enable --now monitor.service
```

### **Ansible Inventory File (`hosts.ini`):**
```ini
[remote]
your-ec2-ip ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/your-key.pem
```

### **Run the Playbook:**
```bash
ansible-playbook -i hosts.ini deploy_script.yml
```

---

## Step 3: Extract and Analyze Data Using Python

### **Python Script (`analyze_data.py`):**
```python
import paramiko
import pandas as pd
import re

# Remote server details
HOST = "your-ec2-ip"
USER = "ubuntu"
KEY_FILE = "~/.ssh/your-key.pem"
LOG_FILE = "/var/log/sys_usage.log"

# Fetch logs from EC2

def fetch_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, key_filename=KEY_FILE)
    sftp = ssh.open_sftp()
    sftp.get(LOG_FILE, "sys_usage.log")
    sftp.close()
    ssh.close()

# Parse the log file
def parse_logs():
    data = []
    with open("sys_usage.log", "r") as f:
        for line in f:
            match = re.match(r'(\d+-\d+-\d+ \d+:\d+:\d+), CPU: ([\d.]+)%, Memory: ([\d.]+)%', line)
            if match:
                timestamp, cpu, memory = match.groups()
                data.append([timestamp, float(cpu), float(memory)])
    df = pd.DataFrame(data, columns=["Timestamp", "CPU_Usage", "Memory_Usage"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

# Analyze data
def analyze_data(df):
    max_cpu = df.loc[df["CPU_Usage"].idxmax()]
    max_mem = df.loc[df["Memory_Usage"].idxmax()]
    print(f"Max CPU Usage: {max_cpu['CPU_Usage']}% at {max_cpu['Timestamp']}")
    print(f"Max Memory Usage: {max_mem['Memory_Usage']}% at {max_mem['Timestamp']}")
    df["Date"] = df["Timestamp"].dt.date
    daily_stats = df.groupby("Date")[["CPU_Usage", "Memory_Usage"]].agg(["mean", "median"])
    print("\nDaily Averages & Medians:")
    print(daily_stats)

if __name__ == "__main__":
    fetch_logs()
    df = parse_logs()
    analyze_data(df)
```

### **Run the Python Script:**
```bash
python3 analyze_data.py
```

---

## **Expected Output**
- **Max CPU & Memory Usage** with corresponding timestamps
- **Daily Average & Median** CPU and memory usage statistics

---

## **Conclusion**
This project automates system performance monitoring on an EC2 instance using a shell script, Ansible for deployment, and Python for analysis. It helps track system resource usage effectively.


