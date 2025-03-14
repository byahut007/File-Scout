import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DirectoryWatcherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Directory Watcher & File Mover")

        # Initialize variables before creating widgets
        self.src_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        self.monitoring = False
        self.observer = None
        self.handler = None

        # Now create widgets (variables are initialized)
        self.create_widgets()

    def create_widgets(self):
        # Source directory section
        source_frame = tk.Frame(self)
        source_frame.pack(padx=10, pady=10)
        tk.Label(source_frame, text="Watch This Directory:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.source_entry = tk.Entry(
            source_frame, textvariable=self.src_dir, state="readonly", width=50
        )
        self.source_entry.grid(row=0, column=1)
        self.source_browse = tk.Button(
            source_frame, text="Browse", command=self.select_source
        )
        self.source_browse.grid(row=0, column=2)

        # Destination directory section
        dest_frame = tk.Frame(self)
        dest_frame.pack(padx=10, pady=10)
        tk.Label(dest_frame, text="Move New Files To:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.dest_entry = tk.Entry(
            dest_frame, textvariable=self.dest_dir, state="readonly", width=50
        )
        self.dest_entry.grid(row=0, column=1)
        self.dest_browse = tk.Button(
            dest_frame, text="Browse", command=self.select_dest
        )
        self.dest_browse.grid(row=0, column=2)

        # Control buttons
        control_frame = tk.Frame(self)
        control_frame.pack(padx=10, pady=10)
        self.start_btn = tk.Button(
            control_frame, text="Start Monitoring", command=self.start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = tk.Button(
            control_frame,
            text="Stop Monitoring",
            state=tk.DISABLED,
            command=self.stop_monitoring,
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Status area
        status_frame = tk.Frame(self)
        status_frame.pack(padx=10, pady=10)
        self.status_text = tk.Text(status_frame, height=5, width=60, state=tk.DISABLED)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(status_frame, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)

    def select_source(self):
        directory = filedialog.askdirectory()
        if directory:
            self.src_dir.set(directory)

    def select_dest(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dest_dir.set(directory)

    def start_monitoring(self):
        src = self.src_dir.get()
        dest = self.dest_dir.get()

        if not src or not dest:
            messagebox.showerror("Error", "Both directories must be selected.")
            return

        if not os.path.exists(src):
            messagebox.showerror("Error", f"Source directory does not exist: {src}")
            return

        if not os.path.exists(dest):
            messagebox.showerror(
                "Error", f"Destination directory does not exist: {dest}"
            )
            return

        # Disable UI elements
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.source_browse.config(state=tk.DISABLED)
        self.dest_browse.config(state=tk.DISABLED)
        self.monitoring = True

        # Start monitoring
        self.handler = MyHandler(dest, self)
        self.observer = Observer()
        self.observer.schedule(self.handler, path=src, recursive=False)
        self.observer.start()
        self.display_status("Monitoring started...")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.handler = None

        # Re-enable UI elements
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.source_browse.config(state=tk.NORMAL)
        self.dest_browse.config(state=tk.NORMAL)
        self.monitoring = False
        self.display_status("Monitoring stopped.")

    def display_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)


class MyHandler(FileSystemEventHandler):
    def __init__(self, destination, app):
        super().__init__()
        self.destination = destination
        self.app = app

    def on_created(self, event):
        if not event.is_directory:
            src_path = event.src_path
            dest_path = os.path.join(self.destination, os.path.basename(src_path))
            try:
                shutil.move(src_path, dest_path)
                self.app.after(
                    0,
                    self.app.display_status,
                    f"File moved: {os.path.basename(src_path)}",
                )
            except Exception as e:
                self.app.after(
                    0, self.app.display_status, f"Error moving file: {str(e)}"
                )


if __name__ == "__main__":
    app = DirectoryWatcherApp()
    app.mainloop()
