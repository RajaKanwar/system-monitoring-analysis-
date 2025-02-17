import paramiko
import pandas as pd
import re

# Remote server details
HOST = "13.126.94.204"
USER = "ubuntu"
KEY_FILE = "/home/raja/Downloads/key.pem"
LOG_FILE = "/var/log/sys_usage.log"

# SSH into the EC2 instance and fetch the log file
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

