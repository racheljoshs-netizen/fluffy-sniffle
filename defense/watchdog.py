import psutil
import time
import os
import sys
import signal

# Configuration
CPU_THRESHOLD = 90.0 # Percentage
MEM_THRESHOLD = 90.0 # Percentage
CHECK_INTERVAL = 2.0 # Seconds
KILL_SWITCH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'KILL_SWITCH.trigger')

# Processes to terminate in emergency
TARGET_PROCESSES = ["python", "firefox", "chrome", "node"]

def emergency_halt(reason):
    print(f"\n[WATCHDOG] !!! EMERGENCY HALT TRIGGERED: {reason} !!!")
    print("[WATCHDOG] TERMINATING OPERATIONS...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process is in target list
            proc_name = proc.info['name'].lower()
            if any(t in proc_name for t in TARGET_PROCESSES):
                # Don't kill self
                if proc.info['pid'] == os.getpid():
                    continue
                
                print(f"[WATCHDOG] Killing {proc.info['name']} (PID: {proc.info['pid']})")
                
                if "--dry-run" not in sys.argv:
                    proc.kill()
                else:
                    print("[WATCHDOG] (Dry Run) Would kill process.")
                
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    print(f"[WATCHDOG] Systems Purged. {killed_count} processes terminated.")
    sys.exit(0)

def main():
    print("[WATCHDOG] Active Defense System Online.")
    print(f"[WATCHDOG] Monitoring CPU > {CPU_THRESHOLD}%, MEM > {MEM_THRESHOLD}%")
    print(f"[WATCHDOG] Kill Switch File: {KILL_SWITCH_FILE}")
    
    if "--dry-run" in sys.argv:
        print("[WATCHDOG] RUNNING IN DRY-RUN MODE")

    # Clean up trigger file if exists on start
    if os.path.exists(KILL_SWITCH_FILE):
        os.remove(KILL_SWITCH_FILE)

    while True:
        try:
            # 1. Check for Manual Kill Switch
            if os.path.exists(KILL_SWITCH_FILE):
                emergency_halt("MANUAL TRIGGER DETECTED")

            # 2. Check System Metrics
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().percent
            
            # Simple heartbeat log every ~10 seconds
            if int(time.time()) % 10 == 0:
                # print(f"[WATCHDOG] Heartbeat: CPU {cpu_usage}% | MEM {mem_usage}%") # Silent heartbeat
                pass

            if cpu_usage > CPU_THRESHOLD:
                # Confirm it's not a spike - wait and check again
                time.sleep(1)
                if psutil.cpu_percent(interval=None) > CPU_THRESHOLD:
                    emergency_halt(f"CRITICAL CPU LOAD ({cpu_usage}%)")
            
            if mem_usage > MEM_THRESHOLD:
                emergency_halt(f"CRITICAL MEMORY LOAD ({mem_usage}%)")
                
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("[WATCHDOG] Deactivating via User Interrupt.")
            break
        except Exception as e:
            print(f"[WATCHDOG] Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
