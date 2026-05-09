import subprocess

class SystemDetector:
    def detect_gpu(self):
        try:
            output = subprocess.check_output(["lspci"], text=True)
            if "NVIDIA" in output:
                return "nvidia"
            elif "AMD" in output:
                return "amd"
            elif "Intel" in output:
                return "intel"
        except:
            pass
        return "unknown"

    def check_internet(self):
        try:
            subprocess.check_call(["ping", "-c", "1", "archlinux.org"],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                                  timeout=3)
            return True
        except:
            return False