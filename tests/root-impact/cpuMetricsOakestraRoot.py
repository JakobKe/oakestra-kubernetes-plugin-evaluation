import paramiko
import time
import os

def run_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    hostname = "10.100.253.57"
    username = "ubuntu"
    key_path = "/Users/jakobkempter/.ssh/id_rsa_ics"
    remote_script = "/home/ubuntu/cpuram"
    remote_output = "/home/ubuntu/cpumemoryusage.csv"
    test = "K0_O3"
    duration = 60  # Duration for each test run in seconds
    cool_down = 30  # Cool down phase in seconds (5 minutes)
    repititions = 5

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, username=username, key_filename=key_path)
    
    for i in range(1, repititions+1):
        local_output = f"./{i}_cpumemoryusage_{test}.csv"
        
        print("Cleaning up old files... ")
        if os.path.exists(local_output):
            os.remove(local_output)
        delete_command = f"rm -f {remote_output}"
        stdout, stderr = run_remote_command(ssh_client, delete_command)
        if stderr:
            print(f"Error deleting old output file: {stderr}")
            continue
        


        print(f"Starting remote script: Run {i} with setup {test} for {duration} seconds...")
        start_command = f"nohup bash {remote_script} {test} > /dev/null 2>&1 & echo $!"
        stdout, stderr = run_remote_command(ssh_client, start_command)
        if stderr:
            print(f"Error starting remote script: {stderr}")
            continue
        pid = stdout.strip()
        #print(f"Remote script started with PID {pid}")

        # Wait for the duration of the test run
        time.sleep(duration)

        # Stop the remote script
        print(f"Stopping remote script (Run {i})...")
        stdout, stderr = run_remote_command(ssh_client, f"kill {pid}")
        if stderr:
            print(f"Error stopping remote script: {stderr}")
            continue

        # Download the result file
        print(f"Downloading the result file (Run {i})...")
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(remote_output, local_output)
        sftp_client.close()
        print(f"File downloaded successfully to {local_output}")

        if i < 5:
            # Cool down phase
            print(f"Cooling down for {cool_down} seconds before next run...")
            time.sleep(cool_down)

    ssh_client.close()
    print("All test runs completed successfully.")

if __name__ == "__main__":
    main()
