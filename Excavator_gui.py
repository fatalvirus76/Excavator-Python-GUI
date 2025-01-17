import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import requests
import json
import os


class ExcavatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Excavator Control Panel")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        # Fonts and Styles
        self.label_font = ("Arial", 10, "bold")
        self.button_font = ("Arial", 9)

        # Server Settings
        server_frame = ttk.LabelFrame(root, text="Server Settings", padding=(10, 10))
        server_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(server_frame, text="Server:", font=self.label_font).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.server_entry = ttk.Entry(server_frame, width=30)
        self.server_entry.insert(0, "127.0.0.1:4067")
        self.server_entry.grid(row=0, column=1, padx=5, pady=5)

        save_settings_btn = ttk.Button(server_frame, text="Save Settings", command=self.save_settings)
        save_settings_btn.grid(row=0, column=2, padx=5, pady=5)

        # Algorithm Selection
        algorithm_frame = ttk.LabelFrame(root, text="Algorithm Selection", padding=(10, 10))
        algorithm_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(algorithm_frame, text="Algorithm:", font=self.label_font).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.algorithm_var = tk.StringVar(root)
        self.algorithm_dropdown = tk.OptionMenu(
            algorithm_frame, self.algorithm_var,
        "daggerhashimoto", "kawpow", "etchash", "autolykos", "zhash", "keccak",  "kheavyhash", "zelhash", "alephium"

        )
        self.algorithm_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.algorithm_var.set("kawpow")

        # Action Buttons
        action_frame = ttk.LabelFrame(root, text="Actions", padding=(10, 10))
        action_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.commands = [
            {"method": "algorithm.add", "label": "Add Algorithm"},
            {"method": "algorithm.remove", "label": "Remove Algorithm"},
            {"method": "algorithm.clear", "label": "Clear Algorithms"},
            {"method": "algorithm.list", "label": "List Algorithms"},
            {"method": "miner.stop", "label": "Stop Miner"},
            {"method": "miner.alive", "label": "Check Miner Alive"},
            {"method": "device.list", "label": "List Devices"},
            {"method": "device.get", "label": "Get Device"},
            {"method": "devices.clear", "label": "Clear Devices"},
            {"method": "device.add", "label": "Add Device Manually"},
            {"method": "info", "label": "Get Info"},
            {"method": "quit", "label": "Quit Excavator"}
        ]

        for idx, command in enumerate(self.commands):
            btn = ttk.Button(
                action_frame,
                text=command["label"],
                command=lambda cmd=command["method"]: self.execute_command(cmd),
                style="TButton"
            )
            btn.grid(row=idx // 2, column=idx % 2, padx=5, pady=5, sticky="ew")

        # Additional Buttons: Run Miner, Run Benchmark
        extra_buttons_frame = ttk.Frame(root)
        extra_buttons_frame.pack(fill="x", padx=10, pady=10)

        run_miner_btn = ttk.Button(extra_buttons_frame, text="Run Miner", command=self.run_miner, style="TButton")
        run_miner_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        run_benchmark_btn = ttk.Button(extra_buttons_frame, text="Run Benchmark", command=self.run_benchmark, style="TButton")
        run_benchmark_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        stop_benchmark_btn = ttk.Button(extra_buttons_frame, text="Stop Miner", command=lambda: self.execute_command("miner.stop"), style="TButton")
        stop_benchmark_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Status Display
        self.status_label = ttk.Label(root, text="Status: Ready", anchor="w", padding=(10, 5))
        self.status_label.pack(fill="x", side="bottom")

        # Store Device UUIDs and Algorithms
        self.device_uuids = []
        self.settings_file = "settings.json"
        self.load_settings()

    def send_request(self, command):
        """Send an HTTP request to the Excavator API."""
        server = self.server_entry.get()
        url = f"http://{server}/api?command={json.dumps(command)}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.update_status(f"Request error: {e}")
            return None

    def save_settings(self):
        """Save server and algorithm settings to a file."""
        settings = {
            "server": self.server_entry.get(),
            "algorithm": self.algorithm_var.get()
        }
        with open(self.settings_file, "w") as file:
            json.dump(settings, file)
        self.update_status("Settings saved successfully!")

    def load_settings(self):
        """Load server and algorithm settings from a file."""
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                self.server_entry.delete(0, tk.END)
                self.server_entry.insert(0, settings.get("server", "127.0.0.1:4067"))
                self.algorithm_var.set(settings.get("algorithm", "kawpow"))

    def update_status(self, message):
        """Update the status label with a message."""
        self.status_label.config(text=f"Status: {message}")

    def execute_command(self, method):
        """Execute specific Excavator commands."""
        params = []
        if method == "algorithm.add":
            selected_algorithm = self.algorithm_var.get()
            params = [selected_algorithm]

        elif method == "algorithm.remove":
            algo_name = simpledialog.askstring("Input", "Enter algorithm name to remove:")
            if algo_name:
                params = [algo_name]

        elif method == "algorithm.clear":
            if messagebox.askyesno("Confirmation", "Are you sure you want to clear all algorithms?"):
                params = []

        elif method == "algorithm.list":
            response = self.send_request({"id": 0, "method": method, "params": []})
            if response and "algorithms" in response:
                algorithms = response["algorithms"]
                details = "\n".join(f"{algo['name']} - Speed: {algo.get('speed', 0):.2f}" for algo in algorithms)
                messagebox.showinfo("Algorithms", details)
            else:
                messagebox.showerror("Error", "Failed to list algorithms.")
            return

        elif method == "device.list":
            response = self.send_request({"id": 0, "method": method, "params": []})
            if response and "devices" in response:
                devices = response["devices"]
                self.device_uuids = [device["uuid"] for device in devices]
                details = "\n".join(f"{device['name']} - UUID: {device['uuid']}" for device in devices)
                messagebox.showinfo("Devices", details)
            else:
                messagebox.showerror("Error", "Failed to list devices.")
            return

        elif method == "device.get":
            device_id = simpledialog.askstring("Input", "Enter device ID or UUID:")
            if device_id:
                params = [device_id]
                response = self.send_request({"id": 0, "method": method, "params": params})
                if response and "device" in response:
                    device_info = json.dumps(response["device"], indent=4)
                    messagebox.showinfo("Device Info", device_info)
                else:
                    self.update_status("Failed to retrieve device info.")
            return

        elif method == "devices.clear":
            self.device_uuids.clear()
            messagebox.showinfo("Devices", "Device list cleared.")
            self.update_status("Device list cleared.")
            return

        elif method == "device.add":
            device_uuid = simpledialog.askstring("Input", "Enter Device UUID:")
            if device_uuid:
                self.device_uuids.append(device_uuid)
                messagebox.showinfo("Device Added", f"Device UUID '{device_uuid}' added.")
                self.update_status(f"Device UUID '{device_uuid}' added.")
            else:
                messagebox.showerror("Error", "Invalid UUID.")
            return

        elif method == "info":
            response = self.send_request({"id": 0, "method": method, "params": []})
            if response:
                info = json.dumps(response, indent=4)
                messagebox.showinfo("System Info", info)
                self.update_status("System info retrieved.")
            else:
                self.update_status("Failed to retrieve system info.")
            return

        elif method == "quit":
            if messagebox.askyesno("Confirmation", "Are you sure you want to quit Excavator?"):
                params = []

        command = {"id": 0, "method": method, "params": params}
        response = self.send_request(command)
        if response and response.get("error") is None:
            self.update_status(f"Command '{method}' executed successfully.")
        else:
            self.update_status(f"Error executing '{method}'.")

    def run_miner(self):
        """Run the miner with selected settings."""
        if not self.device_uuids:
            messagebox.showerror("Error", "No devices available. Please fetch devices first.")
            return

        user = simpledialog.askstring("Input", "Enter username (BTC address):")
        if not user:
            messagebox.showerror("Error", "Username is required.")
            return

        selected_algorithm = self.algorithm_var.get()
        params = {
            "btc_address": user,
            "stratum_url": "nhmp-ssl.eu.nicehash.com:443",
            "devices": [
                {"device_uuid": uuid, "algorithm": selected_algorithm, "params": []}
                for uuid in self.device_uuids
            ]
        }

        command = {"id": 0, "method": "state.set", "params": params}
        response = self.send_request(command)
        if response and response.get("error") is None:
            self.update_status("Mining started successfully.")
        else:
            self.update_status("Failed to start mining.")

    def run_benchmark(self):
        """Run benchmark on selected devices and algorithm."""
        if not self.device_uuids:
            messagebox.showerror("Error", "No devices available. Please fetch devices first.")
            return

        selected_algorithm = self.algorithm_var.get()
        benchmark_results = []

        for uuid in self.device_uuids:
            command = {"id": 0, "method": "algorithm.add", "params": [f"benchmark-{selected_algorithm}"]}
            response = self.send_request(command)
            if response and response.get("error") is None:
                benchmark_results.append(f"Device {uuid}: Benchmark completed successfully.")
            else:
                benchmark_results.append(f"Device {uuid}: Benchmark failed.")

        results = "\n".join(benchmark_results)
        messagebox.showinfo("Benchmark Results", results)
        self.update_status("Benchmark completed.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcavatorGUI(root)
    root.mainloop()
