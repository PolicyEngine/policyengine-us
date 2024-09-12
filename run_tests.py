import psutil
import subprocess
import time
import sys
import io
from datetime import datetime

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def get_process_info(pid):
    try:
        process = psutil.Process(pid)
        return f"PID: {pid}, Name: {process.name()}, Status: {process.status()}"
    except psutil.NoSuchProcess:
        return f"PID: {pid} - Process not found"

def log_message(message, output_file):
    timestamped_message = f"[{get_timestamp()}] {message}"
    print(timestamped_message)
    output_file.write(timestamped_message + "\n")
    output_file.flush()

def log_info(process, output_file):
    memory_info = process.memory_info()
    cpu_percent = process.cpu_percent(interval=1)
    log_message(f"""
Main process: {get_process_info(process.pid)}
Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB
CPU usage: {cpu_percent:.2f}%
Child processes:
""", output_file)
    for child in process.children(recursive=True):
        log_message(f"  {get_process_info(child.pid)}", output_file)
    log_message("---", output_file)

def run_tests():
    command = [
        sys.executable,
        "-m",
        "policyengine_core.scripts.policyengine_command",
        "test",
        "policyengine_us/tests/policy/",
        "-c",
        "policyengine_us"
    ]
    
    log_message(f"Running command: {' '.join(command)}", sys.stdout)
    
    with io.open('test_output.log', 'w', encoding='utf-8') as output_file:
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)

        start_time = time.time()
        while process.poll() is None:
            log_info(psutil.Process(process.pid), output_file)
            
            # Print and log command output
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    log_message(output.strip(), output_file)
            
            if time.time() - start_time > 3600:  # 1 hour timeout
                log_message("Timeout reached", output_file)
                process.terminate()
                break
            
            time.sleep(30)  # Log every 30 seconds

        log_message("Test execution finished", output_file)
        log_message(f"Return code: {process.returncode}", output_file)

if __name__ == "__main__":
    run_tests()