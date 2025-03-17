import json
import asyncio
import threading
import tkinter as tk
from aiohttp import ClientSession
from novelai_api.BanList import BanList
from novelai_api.Tokenizer import Tokenizer
from novelai_api.BiasGroup import BiasGroup
from novelai_api.utils import b64_to_tokens
from novelai_api import NovelAIAPI, NovelAIError
from novelai_api.GlobalSettings import GlobalSettings
from novelai_api.Preset import PREAMBLE, Model, Preset
from tkinter import ttk, scrolledtext, Toplevel, messagebox


class NovelAIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Recast")
        self.root.state('zoomed')  # Start in full screen
        self.root.configure(bg="#15193E")

        # Font/Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Eczar.TLabelframe.Label", font=("Eczar", 20), foreground="#F5F3C2", background="#0E0F21")
        style.configure("Eczar.TLabelframe", background="#0E0F21", bordercolor="#15193E")
        style.configure("Eczar.TLabel", font=("Eczar", 20), foreground="#F5F3C2", background="#0E0F21")
        style.configure("Eczar.TFrame", background="#0E0F21")
        style.configure("Yellow.TRadiobutton", font=("Source Sans 3", 20), foreground="#F5F3C2", background="#0E0F21")
        style.map("Yellow.TRadiobutton", background=[('active', '#15193E')], indicatorcolor=[('selected', '#F5F3C2')])
        style.configure("Yellow.TCombobox", font=("Source Sans 3", 20), fieldbackground="#15193E", foreground="#F5F3C2")
        style.map("Yellow.TCombobox", fieldbackground=[('readonly', "#15193E")], foreground=[('readonly', "#F5F3C2")])
        style.configure("Yellow.TButton", font=("Source Sans 3", 20), foreground="#F5F3C2", background="#0E0F21")
        style.map("Yellow.TButton", background=[('active', '#15193E')])
        style.configure("Menu.TButton", font=("Source Sans 3", 20), foreground="#F5F3C2", background="#15193E")
        style.map("Menu.TButton", background=[('active', '#0E0F21')])
        style.configure("Save.TButton", background="#15193E", foreground="white")
        style.map("Save.TButton", background=[('active', '#367C39')])
        style.configure("Dynamic.TLabel", font=("Source Sans 3", 16), foreground="#FFFFFF", background="#000000")
        style.configure("TEntry", borderwidth=2, relief="groove")
        style.configure("TText", borderwidth=2, relief="groove")

        # Initialize API
        self.api = NovelAIAPI()
        self.model_var = tk.StringVar(value="Erato")

        # --- Top Frame ---
        top_frame = ttk.Frame(root, style="Eczar.TFrame")
        top_frame.pack(fill='x', padx=5, pady=5)

        # Model Selection (Left)
        model_frame = ttk.Frame(top_frame, style="Eczar.TFrame")
        model_frame.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(model_frame, text="Erato", variable=self.model_var, value="Erato", style="Yellow.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(model_frame, text="Kayra", variable=self.model_var, value="Kayra", style="Yellow.TRadiobutton").pack(side=tk.LEFT, padx=5)
        self.model_var.trace('w', self.on_model_change)

        # Instructions and Info Buttons (Center)
        center_button_frame = ttk.Frame(top_frame, style="Eczar.TFrame")
        center_button_frame.pack(side=tk.LEFT, expand=True)  # expand=True to center
        self.instructions_button = ttk.Button(center_button_frame, text="Instructions", command=self.show_instructions, style="Menu.TButton")
        self.instructions_button.pack(side=tk.LEFT, padx=5)
        self.info_button = ttk.Button(center_button_frame, text="Info", command=self.show_info, style="Menu.TButton")
        self.info_button.pack(side=tk.LEFT, padx=5)

        # --- Preset and Prompt Selection (Between Info and Generate) ---
        preset_frame = ttk.Frame(top_frame, style="Eczar.TFrame")
        preset_frame.pack(side=tk.LEFT, fill='x', padx=(5, 5))
        ttk.Label(preset_frame, text="Preset:", style="Eczar.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.preset_combo = ttk.Combobox(preset_frame, state='readonly', style="Yellow.TCombobox")
        self.preset_combo.pack(side=tk.LEFT, fill='x', expand=True)
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset_params)

        prompt_frame = ttk.Frame(top_frame, style="Eczar.TFrame")
        prompt_frame.pack(side=tk.LEFT, fill='x', padx=(5, 5))
        ttk.Label(prompt_frame, text="Prompt:", style="Eczar.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        self.prompt_combo = ttk.Combobox(prompt_frame, state='readonly', style="Yellow.TCombobox")
        self.prompt_combo.pack(side=tk.LEFT, fill='x', expand=True)
        self.prompt_combo.bind('<<ComboboxSelected>>', self.load_prompt)

        # Generate, More, Copy Buttons (Right)
        right_button_frame = ttk.Frame(top_frame, style="Eczar.TFrame")
        right_button_frame.pack(side=tk.RIGHT, padx=(5, 0))
        self.generate_btn = ttk.Button(right_button_frame, text="Generate", command=self.start_generation, style="Yellow.TButton")
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        self.more_btn = ttk.Button(right_button_frame, text="More", command=self.continue_generation, state=tk.DISABLED, style="Yellow.TButton")
        self.more_btn.pack(side=tk.LEFT, padx=5)
        self.copy_btn = ttk.Button(right_button_frame, text="Copy", command=self.copy_to_clipboard, style="Yellow.TButton")
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        # --- Text Input and Output ---
        text_bg = "#000000"
        text_fg = "#FFFFFF"
        input_font_size = 16

        ttk.Label(root, text="Prompt:", style="Eczar.TLabel").pack(anchor='w', padx=10)
        self.prompt_input = scrolledtext.ScrolledText(root, height=3, bg=text_bg, fg=text_fg, insertbackground=text_fg, font=("Source Sans 3", input_font_size), wrap=tk.WORD)
        self.prompt_input.pack(padx=10, pady=5, fill='x')

        # --- Input/Output Frame ---
        io_frame = ttk.Frame(root, style="Eczar.TFrame")
        io_frame.pack(padx=10, pady=0, fill='both', expand=True)
        io_frame.columnconfigure(0, weight=1)
        io_frame.rowconfigure(1, weight=1)
        io_frame.rowconfigure(3, weight=1)

        # --- Input Text and Intro --- (Inside io_frame)
        input_label_frame = ttk.Frame(io_frame, style="Eczar.TFrame")
        input_label_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(input_label_frame, text="Input Text:", style="Eczar.TLabel").pack(side=tk.LEFT, anchor='w')
        self.field1_label = ttk.Label(input_label_frame, text="", style="Dynamic.TLabel", wraplength=400)
        self.field1_label.pack(side=tk.RIGHT, padx=(5, 0), fill='x')
        ttk.Label(input_label_frame, text="Intro:", style="Eczar.TLabel").pack(side=tk.RIGHT, padx=(5, 0), anchor='e')

        self.input_text = scrolledtext.ScrolledText(io_frame, height=5, bg=text_bg, fg=text_fg, insertbackground=text_fg, font=("Source Sans 3", input_font_size), wrap=tk.WORD, relief="groove", borderwidth=2)
        self.input_text.grid(row=1, column=0, sticky="nsew")

        # --- Output and Outro --- (Inside io_frame)
        output_label_frame = ttk.Frame(io_frame, style="Eczar.TFrame")
        output_label_frame.grid(row=2, column=0, sticky="ew")
        ttk.Label(output_label_frame, text="Output:", style="Eczar.TLabel").pack(side=tk.LEFT, anchor='w')
        self.field2_label = ttk.Label(output_label_frame, text="", style="Dynamic.TLabel", wraplength=400)
        self.field2_label.pack(side=tk.RIGHT, padx=(5, 0), fill='x')
        ttk.Label(output_label_frame, text="Outro:", style="Eczar.TLabel").pack(side=tk.RIGHT, padx=(5, 0), anchor='e')

        self.output_text = scrolledtext.ScrolledText(io_frame, height=5, bg=text_bg, fg=text_fg, font=("Source Sans 3", input_font_size), wrap=tk.WORD, relief="groove", borderwidth=2)
        self.output_text.grid(row=3, column=0, sticky="nsew")

        # Authentication setup
        self.credentials = self.load_credentials()
        self.login_thread = threading.Thread(target=self.run_async_login)
        self.login_thread.start()

        # Load initial data
        self.load_presets()
        self.load_prompts()

        # Initialize accumulated_output
        self.accumulated_output = ""

    def show_instructions(self):
        instructions_window = Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry("500x250")
        instructions_window.configure(bg="#15193E")

        try:
            with open("instructions.txt", "r") as f:
                instructions = f.read()
        except FileNotFoundError:
            instructions = "Error: instructions.txt not found."

        instructions_text = scrolledtext.ScrolledText(instructions_window, wrap=tk.WORD, bg="#0E0F21", fg="#F5F3C2", font=("Source Sans 3", 12))
        instructions_text.insert(tk.END, instructions)
        instructions_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        instructions_text.config(state=tk.DISABLED)

    def show_info(self):
        info_window = Toplevel(self.root)
        info_window.title("App Information")
        info_window.geometry("500x180")
        info_window.configure(bg="#15193E")

        try:
            with open("info.json", "r") as f:
                info_data = json.load(f)
            info = (f"Title: {info_data['title']}\n"
                    f"Version: {info_data['version']}\n"
                    f"Author: {info_data['author']}\n"
                    f"Credits: {info_data['credits']}\n"
                    f"Links: {info_data['links']}\n"
                    f"My repo: {info_data['my repo']}")
        except FileNotFoundError:
            info = "Error: info.json not found."
        except json.JSONDecodeError:
            info = "Error: info.json contains invalid JSON."
        except KeyError as e:
            info = f"Error: Missing key in info.json: {e}"

        info_text = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, bg="#0E0F21", fg="#F5F3C2", font=("Source Sans 3", 12))
        info_text.insert(tk.END, info)
        info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        info_text.config(state=tk.DISABLED)

    async def __aenter__(self):
        self.session = ClientSession()
        await self.session.__aenter__()
        self.api.attach_session(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)
        self.api.detach_session()

    def load_credentials(self):
        try:
            with open('credentials.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            self.show_error(f"Credentials error: {str(e)}")
            return None

    def run_async_login(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.perform_login())

    async def perform_login(self):
        try:
            async with self as api_handler:
                await api_handler.api.high_level.login(
                    self.credentials['username'],
                    self.credentials['password']
                )
            print("Login successful")
            self.root.after(0, lambda: self.update_output("Login Successful"))
            self.root.after(0, self.enable_buttons)
        except Exception as e:
            self.root.after(0, self.show_error, f"Login failed: {str(e)}")

    async def generate_text(self, is_continue=False):
        try:
            model_name = self.model_var.get()
            preset_name = self.preset_combo.get()
            model = Model[model_name]
            preset = Preset.from_official(model, preset_name)

            if preset and hasattr(preset, "repetition_penalty_default_whitelist"):
                preset.rep_pen_whitelist = preset.repetition_penalty_default_whitelist
                delattr(preset, "repetition_penalty_default_whitelist")

            global_settings = GlobalSettings()

            prompt = self.prompt_input.get(1.0, tk.END).strip()
            field1 = self.field1_label.cget("text")
            input_text = self.input_text.get(1.0, tk.END).strip()
            field2 = self.field2_label.cget("text")

            if is_continue:
                full_prompt = f"{prompt}\n{field1}\n{input_text}\n{field2}\n{self.accumulated_output}"
            else:
                full_prompt = f"{prompt}\n{field1}\n{input_text}\n{field2}"

            full_prompt = PREAMBLE[model] + full_prompt
            tokenized_prompt = await asyncio.to_thread(Tokenizer.encode, model, full_prompt)

            if model == Model.Erato:
                bad_words = BanList({"sequence": "test"})
                bias_group = BiasGroup(0.5)
                bias_group.add({"sequence": "example"})
                biases = [bias_group]
            else:
                bad_words = BanList("test")
                bias_group = BiasGroup(0.5)
                bias_group.add("example")
                biases = [bias_group]

            async with self as api_handler:
                response = await api_handler.api.high_level.generate(
                    prompt=tokenized_prompt,
                    model=model,
                    preset=preset,
                    global_settings=global_settings,
                    bad_words=bad_words,
                    biases=biases,
                    remove_input=True
                )

            generated_tokens = response['output']
            token_ids = b64_to_tokens(generated_tokens, 2 if model == Model.Kayra else 4)
            generated_text = await asyncio.to_thread(Tokenizer.decode, model, token_ids)


            if is_continue:
                self.accumulated_output += generated_text
                self.root.after(0, self.append_output, generated_text)
            else:
                self.accumulated_output = generated_text
                self.root.after(0, self.update_output, generated_text)

        except NovelAIError as e:
            self.root.after(0, self.show_error, f"NovelAI Error: {e.message}")
        except Exception as e:
            self.root.after(0, self.show_error, f"Unexpected Error: {str(e)}")
        finally:
            self.root.after(0, self.enable_buttons)

    def start_generation(self):
        self.disable_buttons()
        threading.Thread(target=self.run_async_generate).start()

    def run_async_generate(self, is_continue=False):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.generate_text(is_continue))

    def update_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)

    def append_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)

    def enable_buttons(self):
        self.generate_btn.config(state=tk.NORMAL)
        self.more_btn.config(state=tk.NORMAL)

    def disable_buttons(self):
        self.generate_btn.config(state=tk.DISABLED)
        self.more_btn.config(state=tk.DISABLED)

    def show_error(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Error: {message}")

    def continue_generation(self):
        self.disable_buttons()
        threading.Thread(target=self.run_async_generate, args=(True,)).start()

    def load_presets(self):
        self.presets = {
            "Erato": [],
            "Kayra": []
        }

        erato_presets = Preset[Model.Erato]
        self.presets["Erato"] = [preset.name for preset in erato_presets]

        kayra_presets = Preset[Model.Kayra]
        self.presets["Kayra"] = [preset.name for preset in kayra_presets]

        self.update_preset_combo()
        self.set_default_presets()

    def set_default_presets(self):
        current_model = self.model_var.get()
        if current_model == "Erato":
            default_preset = "Golden Arrow"
        elif current_model == "Kayra":
            default_preset = "Fresh Coffee"
        else:
            default_preset = None

        if default_preset and default_preset in self.preset_combo['values']:
            self.preset_combo.set(default_preset)
        elif self.preset_combo['values']:
            self.preset_combo.current(0)

    def update_preset_combo(self):
        current_model = self.model_var.get()
        presets_for_model = self.presets.get(current_model, [])
        self.preset_combo['values'] = presets_for_model

    def load_prompt(self, event):
        selected_prompt = self.prompt_combo.get()
        if selected_prompt == "Custom":
            self.show_custom_prompt_window()
        else:
            if selected_prompt in self.prompts:
                self.prompt_input.delete(1.0, tk.END)
                self.prompt_input.insert(tk.END, self.prompts[selected_prompt])
            self.load_prompt_fields(selected_prompt)

    def show_custom_prompt_window(self):
        custom_window = Toplevel(self.root)
        custom_window.title("Create Custom Prompt")
        custom_window.geometry("600x500")
        custom_window.configure(bg="#15193E")
        custom_window.grab_set()

        ttk.Label(custom_window, text="Custom Prompt Name:", style="Eczar.TLabel").pack(anchor='w', padx=10, pady=(10, 0))
        custom_prompt_name = tk.Entry(custom_window, bg="#0E0F21", fg="#F5F3C2", insertbackground="#F5F3C2", font=("Source Sans 3", 12))
        custom_prompt_name.pack(padx=10, pady=5, fill='x', expand=True)

        ttk.Label(custom_window, text="Custom Prompt:", style="Eczar.TLabel").pack(anchor='w', padx=10)
        custom_prompt_text = tk.Text(custom_window, height=5, bg="#0E0F21", fg="#F5F3C2", insertbackground="#F5F3C2", font=("Source Sans 3", 12))
        custom_prompt_text.pack(padx=10, pady=5, fill='both', expand=True)

        ttk.Label(custom_window, text="Custom Intro:", style="Eczar.TLabel").pack(anchor='w', padx=10)
        custom_field1_input = tk.Text(custom_window, height=1, bg="#0E0F21", fg="#F5F3C2", insertbackground="#F5F3C2", font=("Source Sans 3", 12))
        custom_field1_input.pack(padx=10, pady=5, fill='both', expand=True)

        ttk.Label(custom_window, text="Custom Outro:", style="Eczar.TLabel").pack(anchor='w', padx=10)
        custom_field2_input = tk.Text(custom_window, height=1, bg="#0E0F21", fg="#F5F3C2", insertbackground="#F5F3C2", font=("Source Sans 3", 12))
        custom_field2_input.pack(padx=10, pady=5, fill='both', expand=True)

        def save_custom():
            prompt_name = custom_prompt_name.get().strip()
            prompt_text = custom_prompt_text.get(1.0, tk.END).strip()
            field1_text = custom_field1_input.get(1.0, tk.END).strip()
            field2_text = custom_field2_input.get(1.0, tk.END).strip()

            if not prompt_name:
                messagebox.showerror("Error", "Please enter a name for your custom prompt.")
                return

            self.prompts[prompt_name] = prompt_text

            try:
                with open('prompts.json', 'w') as f:
                    json.dump(self.prompts, f, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save to prompts.json: {e}")
                return

            self.prompt_fields[prompt_name] = {
                "field1": field1_text,
                "field2": field2_text
            }

            try:
                with open('prompt_fields.json', 'w') as f:
                    json.dump(self.prompt_fields, f, indent=4)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save to prompt_fields.json: {e}")
                return

            self.prompt_combo['values'] = list(self.prompts.keys()) + ["Custom"]
            self.prompt_combo.set(prompt_name)
            messagebox.showinfo("Success", "Custom prompt saved successfully!")
            custom_window.destroy()

        save_button = ttk.Button(custom_window, text="Save Custom Prompt", command=save_custom, style="Save.TButton")
        save_button.pack(pady=10)

    def load_preset_params(self, event=None):
        model_name = self.model_var.get()
        preset_name = self.preset_combo.get()
        model = Model[model_name]
        preset = Preset.from_official(model, preset_name)

        if preset:
            print(f"Selected Preset: {preset.name}")
            print("Parameters:", preset.to_settings())

    def on_model_change(self, *args):
        self.update_preset_combo()
        self.set_default_presets()

    def load_prompts(self):
        try:
            with open('prompts.json', 'r') as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            self.prompts = {"Summarize": "Summarize the following text"}
            with open('prompts.json', 'w') as f:
                json.dump(self.prompts, f)

        if "Custom" not in self.prompts:
            self.prompts["Custom"] = "Your prompt. Start with [ ATTGS] or select a premade."

        self.prompt_combo['values'] = list(self.prompts.keys())
        self.prompt_combo.set("Custom")
        self.prompt_input.delete(1.0, tk.END)
        self.prompt_input.insert(tk.END, self.prompts.get(self.prompt_combo.get(), ""))
        self.load_prompt_fields()
        self.accumulated_output = ""

    def load_prompt_fields(self, selected_prompt=None):
        try:
            with open("prompt_fields.json", "r") as f:
                self.prompt_fields = json.load(f)
        except FileNotFoundError:
            self.prompt_fields = {}
            print("Error: prompt_fields.json not found.")
            return
        except json.JSONDecodeError:
            print("Error: prompt_fields.json contains invalid JSON.")
            return

        if selected_prompt is None:
            selected_prompt = self.prompt_combo.get()

        field_data = self.prompt_fields.get(selected_prompt, {"field1": "", "field2": ""})
        self.field1_label.config(text=field_data["field1"])
        self.field2_label.config(text=field_data["field2"])

    def copy_to_clipboard(self):
        try:
            output_content = self.output_text.get(1.0, tk.END).strip()
            if output_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(output_content)
                self.root.update()
                print("Copied to clipboard:", output_content)
            else:
                print("No content in Output to copy.")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NovelAIGUI(root)
    root.mainloop()