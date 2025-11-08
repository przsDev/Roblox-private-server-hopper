import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser
import sys
import time
import pygetwindow as gw
import threading
import requests
from bs4 import BeautifulSoup
import pyperclip
import pyautogui

WINDOW_WIDTH = 430
WINDOW_HEIGHT = 550

class RobloxLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox serverlist hopper")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        self.selected_file = None
        self.links = []
        self.current_index = -1
        self.is_hopping = False
        self.has_joined = False
        self.dark_mode = False
        self.title_label = tk.Label(root, text="Roblox Auto Launcher", font=("Arial", 20, "bold"), bg='white')
        self.title_label.pack(pady=20)
        self.file_label = tk.Label(root, text="No file selected", font=("Arial", 12), bg='white', fg='gray')
        self.file_label.pack(pady=10)
        self.browse_button = tk.Button(root, text="Select Links File", font=("Arial", 12),
                                       command=self.browse_file, width=20, height=2, bg='#f0f0f0', fg='black')
        self.browse_button.pack(pady=5)
        self.doc_button = tk.Button(root, text="Paste Google Doc Link", font=("Arial", 12),
                                    command=self.paste_google_doc, width=20, height=2, bg='#9C27B0', fg='white')
        self.doc_button.pack(pady=5)
        self.progress_label = tk.Label(root, text="", font=("Arial", 10), bg='white', fg='gray')
        self.progress_label.pack(pady=5)
        self.status_label = tk.Label(root, text="Ready - Please select a links file or Google Doc", font=("Arial", 11), bg='white', fg='blue')
        self.status_label.pack(pady=10)
        self.join_button = tk.Button(root, text="Join Server", font=("Arial", 14, "bold"),
                                     command=self.join_first_server, width=20, height=2, bg='#2196F3', fg='white', state='disabled')
        self.join_button.pack(pady=10)
        self.instructions_label = tk.Label(root, text="Select a .txt file or Google Doc with Roblox links (roblox.com)", font=("Arial", 9), bg='white', fg='gray')
        self.instructions_label.pack(pady=10)
        self.nav_frame = tk.Frame(root, bg='white')
        self.prev_button = tk.Button(self.nav_frame, text="← Previous", font=("Arial", 12, "bold"), command=self.prev_server, width=15, height=2, bg='#FF9800', fg='white', state='disabled')
        self.prev_button.pack(side='left', padx=5)
        self.next_button = tk.Button(self.nav_frame, text="Next →", font=("Arial", 12, "bold"), command=self.next_server, width=15, height=2, bg='#4CAF50', fg='white', state='disabled')
        self.next_button.pack(side='left', padx=5)
        self.mode_button = tk.Button(root, text="Enable Dark Mode", font=("Arial", 10, "bold"), command=self.toggle_dark_mode, width=20, height=2, bg='#555555', fg='white')
        self.mode_button.pack(pady=10)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            bg_color = '#161616'
            text_color = 'white'
            button_bg_default = '#333333'
            button_fg_default = 'white'
            self.mode_button.config(text="Enable Light Mode")
        else:
            bg_color = 'white'
            text_color = 'black'
            button_bg_default = '#f0f0f0'
            button_fg_default = 'black'
            self.mode_button.config(text="Enable Dark Mode")
        self.root.configure(bg=bg_color)
        self.nav_frame.configure(bg=bg_color)
        for lbl in [self.title_label, self.file_label, self.progress_label, self.status_label, self.instructions_label]:
            lbl.config(bg=bg_color, fg=text_color)
        for btn in [self.browse_button, self.join_button, self.prev_button, self.next_button, self.mode_button, self.doc_button]:
            if btn in [self.join_button]:
                btn.config(fg='white', bg='#2196F3')
            elif btn in [self.prev_button]:
                btn.config(fg='white', bg='#FF9800')
            elif btn in [self.next_button]:
                btn.config(fg='white', bg='#4CAF50')
            elif btn == self.mode_button:
                btn.config(fg=button_fg_default, bg=button_bg_default)
            elif btn == self.doc_button:
                btn.config(fg='white', bg='#9C27B0')
            else:
                btn.config(bg=button_bg_default, fg=button_fg_default)

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select Links File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            self.selected_file = filename
            self.load_links_from_file()
            self.file_label.config(text=f"Selected: {filename.split('/')[-1]}", fg='black' if not self.dark_mode else 'white')

    def load_links_from_file(self):
        try:
            with open(self.selected_file, 'r') as f:
                self.links = [line.strip() for line in f if line.strip() and line.strip().startswith('http') and 'roblox.com' in line]
            self.post_links_load()
        except Exception as e:
            self.status_label.config(text=f"✗ Error loading file", fg='red')
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    def paste_google_doc(self):
        doc_url = simpledialog.askstring("Google Doc Link", "Paste the Google Doc link here:")
        if not doc_url:
            return
        self.status_label.config(text="Fetching links from Google Doc...", fg='blue')
        threading.Thread(target=lambda: self.load_links_from_doc(doc_url), daemon=True).start()

    def load_links_from_doc(self, url):
        try:
            if '/edit' in url:
                url = url.split('/edit')[0] + '/export?format=html'
            elif '/view' in url:
                url = url.split('/view')[0] + '/export?format=html'
            response = requests.get(url)
            if response.status_code != 200:
                self.root.after(0, lambda: self.status_label.config(text=f"✗ Failed to fetch Google Doc", fg='red'))
                return
            soup = BeautifulSoup(response.text, 'html.parser')
            a_tags = soup.find_all('a', href=True)
            self.links = [tag['href'].strip() for tag in a_tags if 'roblox.com' in tag['href'] and tag['href'].startswith('http')]
            if not self.links:
                self.root.after(0, lambda: self.status_label.config(text="✗ No valid Roblox links found in Google Doc", fg='red'))
                messagebox.showwarning("Warning", "No valid Roblox links found in the document!")
                return
            self.post_links_load()
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"✗ Error fetching Google Doc", fg='red'))
            messagebox.showerror("Error", f"Could not fetch Google Doc:\n{e}")

    def post_links_load(self):
        if self.links:
            self.status_label.config(text=f"✓ Loaded {len(self.links)} Roblox links - Ready to join!", fg='green')
            self.join_button.config(state='normal')
            self.progress_label.config(text="")
            self.current_index = -1
            self.has_joined = False
        else:
            self.status_label.config(text="✗ No valid links found", fg='red')
            messagebox.showwarning("Warning", "No valid Roblox links found!")

    def update_progress(self):
        if self.has_joined and self.links:
            self.progress_label.config(text=f"Server {self.current_index + 1} of {len(self.links)}", fg='white' if self.dark_mode else 'black')
        else:
            self.progress_label.config(text="")

    def update_button_states(self):
        if not self.links:
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
            self.join_button.config(state='disabled')
            return
        if not self.has_joined:
            self.join_button.config(state='normal')
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
        else:
            self.prev_button.config(state='normal' if self.current_index > 0 else 'disabled')
            self.next_button.config(state='normal' if self.current_index < len(self.links) - 1 else 'disabled')
        self.update_progress()

    def find_browser_window(self):
        try:
            windows = gw.getAllWindows()
            for window in windows:
                title_lower = window.title.lower()
                if any(browser in title_lower for browser in ['chrome', 'firefox', 'edge', 'safari', 'browser']):
                    return window
            return None
        except Exception as e:
            print(f"Error finding browser: {e}")
            return None

    def close_browser_tab(self):
        try:
            window = self.find_browser_window()
            if window:
                window.activate()
                time.sleep(0.5)
                if sys.platform == 'darwin':
                    pyautogui.hotkey('command', 'w')
                else:
                    pyautogui.hotkey('ctrl', 'w')
                time.sleep(0.5)
        except Exception as e:
            print(f"Error closing tab: {e}")

    def check_url_for_error(self):
        try:
            window = self.find_browser_window()
            if not window:
                return False
            window.activate()
            time.sleep(0.5)
            if sys.platform == 'darwin':
                pyautogui.hotkey('command', 'l')
                pyautogui.hotkey('command', 'c')
            else:
                pyautogui.hotkey('ctrl', 'l')
                pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            url = pyperclip.paste()
            if '/request-error?code=' in url:
                return True
            return False
        except:
            return False

    def open_server_thread(self, index, is_first=False):
        try:
            self.is_hopping = True
            self.root.after(0, lambda: self.join_button.config(state='disabled'))
            self.root.after(0, lambda: self.prev_button.config(state='disabled'))
            self.root.after(0, lambda: self.next_button.config(state='disabled'))
            if not is_first:
                self.root.after(0, lambda: self.status_label.config(text="Closing previous tab...", fg='orange'))
                self.close_browser_tab()
                time.sleep(1)
            if index < 0 or index >= len(self.links):
                self.root.after(0, lambda: self.status_label.config(text="Invalid server index!", fg='red'))
                return
            link = self.links[index]
            self.current_index = index
            self.root.after(0, lambda: self.status_label.config(text=f"Opening server {self.current_index + 1}/{len(self.links)}...", fg='blue'))
            webbrowser.open(link)
            time.sleep(1)
            if self.check_url_for_error():
                self.root.after(0, lambda: self.status_label.config(text=f"✗ Server {self.current_index + 1} invalid, skipping...", fg='red'))
                time.sleep(0.5)
                if self.current_index < len(self.links) - 1:
                    threading.Thread(target=lambda: self.open_server_thread(self.current_index + 1), daemon=True).start()
                return
            window = self.find_browser_window()
            if window:
                window.activate()
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(0.5)
            else:
                self.root.after(0, lambda: self.status_label.config(text="⚠ Browser window not found - please press Enter manually", fg='orange'))
            if is_first:
                self.has_joined = True
                self.root.after(0, self.switch_to_navigation_ui)
            self.root.after(0, lambda: self.status_label.config(text=f"✓ Server {self.current_index + 1}/{len(self.links)} opened!", fg='green'))
        finally:
            self.is_hopping = False
            self.root.after(0, self.update_button_states)

    def switch_to_navigation_ui(self):
        self.join_button.pack_forget()
        self.nav_frame.pack(pady=10)
        self.mode_button.pack_forget()
        self.mode_button.pack(pady=10)
        self.update_button_states()

    def join_first_server(self):
        if self.is_hopping:
            messagebox.showinfo("Info", "Operation in progress, please wait...")
            return
        if not self.links:
            messagebox.showwarning("Warning", "Please select a links file or Google Doc first!")
            return
        threading.Thread(target=lambda: self.open_server_thread(0, is_first=True), daemon=True).start()

    def next_server(self):
        if self.is_hopping:
            messagebox.showinfo("Info", "Operation in progress, please wait...")
            return
        if not self.links:
            messagebox.showwarning("Warning", "Please select a links file or Google Doc first!")
            return
        if self.current_index >= len(self.links) - 1:
            messagebox.showinfo("Info", "You're already at the last server!")
            return
        threading.Thread(target=lambda: self.open_server_thread(self.current_index + 1), daemon=True).start()

    def prev_server(self):
        if self.is_hopping:
            messagebox.showinfo("Info", "Operation in progress, please wait...")
            return
        if not self.links:
            messagebox.showwarning("Warning", "Please select a links file or Google Doc first!")
            return
        if self.current_index <= 0:
            messagebox.showinfo("Info", "You're already at the first server!")
            return
        threading.Thread(target=lambda: self.open_server_thread(self.current_index - 1), daemon=True).start()

def main():
    root = tk.Tk()
    app = RobloxLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
