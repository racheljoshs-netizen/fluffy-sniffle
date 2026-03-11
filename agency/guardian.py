import subprocess
import time
import sys
import os
import logging
from pathlib import Path

# Setup logging
LOG_DIR = Path(r"E:\0x\logs\agency")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [GUARDIAN] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "guardian.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class MothershipGuardian:
    def __init__(self):
        self.processes = {
            "Command-Bar": {
                "cmd": [sys.executable, "agency/command_bar.py"],
                "process": None,
                "restart_delay": 5,
                "last_start": 0
            },
            "Telegram-Commander": {
                "cmd": [sys.executable, "telegram_commander.py"],
                "process": None,
                "restart_delay": 5,
                "last_start": 0
            }
        }

    def start_process(self, name):
        spec = self.processes[name]
        logging.info(f"Igniting {name}...")
        try:
            # We use a shell-free popen to ensure we can kill it later
            spec["process"] = subprocess.Popen(
                spec["cmd"],
                cwd=str(Path(__file__).parent.parent), # Run from project root
                stdout=None, # Inherit stdout for visibility in terminal
                stderr=None
            )
            spec["last_start"] = time.time()
            logging.info(f"{name} active (PID: {spec['process'].pid})")
        except Exception as e:
            logging.error(f"Failed to start {name}: {e}")

    def monitor(self):
        logging.info("Mothership Guardian Online. Monitoring Cluster Stability.")
        
        # Initial stagger
        for name in self.processes:
            self.start_process(name)
            time.sleep(5) # Stagger ignition to prevent PSU spikes

        try:
            while True:
                for name, spec in self.processes.items():
                    # Check if process is still running
                    if spec["process"].poll() is not None:
                        exit_code = spec["process"].returncode
                        logging.warning(f"CRASH DETECTED: {name} exited with code {exit_code}")
                        
                        # Anti-spinlock: Don't restart too fast if it's failing instantly
                        if time.time() - spec["last_start"] < 10:
                            logging.error(f"{name} is failing too quickly. Backing off.")
                            time.sleep(10)
                        
                        logging.info(f"Recovering {name}...")
                        self.start_process(name)
                
                time.sleep(2) # Monitor loop frequency
        except KeyboardInterrupt:
            logging.info("Guardian Shutdown sequence initiated.")
            for name, spec in self.processes.items():
                if spec["process"]:
                    logging.info(f"Terminating {name}...")
                    spec["process"].terminate()
            logging.info("Guardian Offline.")

if __name__ == "__main__":
    guardian = MothershipGuardian()
    guardian.monitor()
