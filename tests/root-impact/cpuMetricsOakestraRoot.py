import paramiko
import time
import os

def run_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    hostname = "10.100.253.175"
    username = "ubuntu"
    key_path = "/Users/jakobkempter/.ssh/id_rsa_ics"
    remote_script = "/home/ubuntu/cpuram"
    remote_output = "/home/ubuntu/cpumemoryusage.csv"
    local_output = "./cpumemoryusage.csv"  # Replace with your desired local directory

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, username=username, key_filename=key_path)

    print("Starting remote script...")
    start_command = f"nohup bash {remote_script} > /dev/null 2>&1 & echo $!"
    stdout, stderr = run_remote_command(ssh_client, start_command)
    if stderr:
        print(f"Error starting remote script: {stderr}")
        return
    pid = stdout
    print(f"Remote script started with PID {pid}")


    # Wait for 5 minutes
    print("Waiting for 5 minutes...")
    time.sleep(5 * 1)

    # Stop the remote script
    print("Stopping remote script...")
    stdout, stderr = run_remote_command(ssh_client, f"kill -SIGINT {pid}")
    if stderr:
        print(f"Error stopping remote script: {stderr}")
        return

    # Download the result file
    print("Downloading the result file...")
    sftp_client = ssh_client.open_sftp()
    sftp_client.get(remote_output, local_output)
    sftp_client.close()
    ssh_client.close()

    print(f"File downloaded successfully to {local_output}")

if __name__ == "__main__":
    main()
