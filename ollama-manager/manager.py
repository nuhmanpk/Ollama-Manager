import subprocess
import platform
import os
import signal
import threading


class OllamaManager:
    def __init__(self):
        self.server_process = None

    def init(self):
        """Check if Ollama is installed, install it if necessary, and start the server."""
        if not self.is_ollama_installed():
            self.install_ollama()
        self.start_server()

    def is_ollama_installed(self):
        """Check if Ollama is installed."""
        try:
            subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Ollama is installed.")
            return True
        except FileNotFoundError:
            print("❌ Ollama is not installed.")
            return False

    def install_ollama(self):
        """Install Ollama."""
        print("🚀 Installing Ollama...")
        system_type = platform.system()
        if system_type == "Linux":
            try:
                subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", check=True, shell=True)
                print("✅ Ollama installation completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation failed: {e}")
                raise
        else:
            raise RuntimeError(f"Unsupported operating system: {system_type}")

    def start_server(self):
        """Start the Ollama server."""
        if self.server_process:
            print("⚠️ Server is already running.")
            return
        print("🚀 Starting Ollama server...")
        self.server_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        threading.Thread(target=self.stream_output, args=(self.server_process,), daemon=True).start()
        print("✅ Ollama server started.")

    def stop_server(self):
        """Stop the Ollama server."""
        if self.server_process:
            print("🛑 Stopping Ollama server...")
            os.kill(self.server_process.pid, signal.SIGTERM)
            self.server_process.wait()
            self.server_process = None
            print("✅ Ollama server stopped.")
        else:
            print("⚠️ No server is running.")

    def run_command(self, command):
        """Run an Ollama command with real-time output."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.stream_output(process)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing command '{' '.join(command)}': {e}")

    def pull_model(self, model_name):
        """Pull a model."""
        print(f"📥 Pulling model: {model_name}")
        self.run_command(["ollama", "pull", model_name])

    def run_model(self, model_name):
        """Run a model."""
        print(f"🏃 Running model: {model_name}")
        self.run_command(["ollama", "run", model_name])

    def list_models(self):
        """List all available models."""
        print("📋 Listing available models:")
        self.run_command(["ollama", "list"])

    def list_running_models(self):
        """List all running models."""
        print("📋 Listing running models:")
        self.run_command(["ollama", "ps"])

    def stop_model(self, model_name):
        """Stop a running model."""
        print(f"🛑 Stopping model: {model_name}")
        self.run_command(["ollama", "stop", model_name])

    def remove_model(self, model_name):
        """Remove a model."""
        print(f"🗑️ Removing model: {model_name}")
        self.run_command(["ollama", "rm", model_name])

    @staticmethod
    def stream_output(process):
        """Stream the output of a subprocess in real-time."""
        for line in process.stdout:
            print(line.strip())
        for line in process.stderr:
            print(f"⚠️ {line.strip()}")
