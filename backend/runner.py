import subprocess
from PySide6.QtCore import QObject, Signal

class CommandRunner(QObject):
    output_signal = Signal(str)
    finished_signal = Signal(int)

    def run_command(self, cmd: list[str]):
        self.output_signal.emit(f"$ {' '.join(cmd)}\n")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                self.output_signal.emit(line.strip())
            process.wait()
            self.finished_signal.emit(process.returncode)
        except Exception as e:
            self.output_signal.emit(f"Error: {e}")
            self.finished_signal.emit(1)