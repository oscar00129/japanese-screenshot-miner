import tkinter as tk
import tkinter.font as tkfont
import shutil, sys

from PIL import Image, ImageTk
from tkinter import messagebox
from pathlib import Path
from datetime import date
from ocr.ocr_processor import OCRProcessor
from csv_processor.csv_processor import CSVProcessor
from tts_processor.tts_processor import TTSProcessor
from config.config import Config

class ImageSelector:
    def __init__(self, image_paths:list[Path], today:date, config:Config):
        self.image_paths = image_paths
        self.today = today
        self.config = config
        self.current_index = 0
        self.root = tk.Tk()
        self.ocr = OCRProcessor()
        self.csv = CSVProcessor(self.today)
        self.tts = TTSProcessor()

        self.set_cursor_coordinates()
        self.set_sizes()
        self.make_interface()
        self.load_current_image()

    def run(self):
        self.root.mainloop()

    def set_cursor_coordinates(self):
        self.start_x = None
        self.start_y = None
        self.rect = None

    def set_sizes(self):
        self.scale_factor = 2
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.half_screen_width = self.shrink(self.screen_width)
        self.half_screen_height = self.shrink(self.screen_height)

    def make_interface(self):
        self.root.title("Please, select the text to mine")

        self.canvas = tk.Canvas(
            self.root,
            width=self.half_screen_width,
            height=self.half_screen_height
        )
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.pack(fill="both", expand=True)

        self.skip_button = tk.Button(
            self.root,
            text="Skip",
            command=self.next_image
        )
        self.skip_button.pack()
    
    def load_current_image(self):
        try:
            self.current_path = self.image_paths[self.current_index]
        except IndexError:
            messagebox.showerror("Error", "No more screenshots!")
            self.root.destroy()
            sys.exit(1)
        self.original_image = Image.open(self.current_path)
        self.display_image = self.resize_img(self.original_image)

        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
    
    def next_image(self):
        self.current_index  += 1

        if self.current_index >= len(self.image_paths):
            print("No more images")
            self.root.destroy()
            return
        
        self.canvas.delete("all")
        self.load_current_image()
    
    def shrink(self, value:int) -> int:
        return int(value / self.scale_factor)
    
    def scale(self, value:int) -> int:
        return int(value * self.scale_factor)

    def resize_img(self, img):
        width, height = img.size
        return img.resize((
            self.shrink(width),
            self.shrink(height)
        ))

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x, self.start_y,
            outline="red"
        )

    def on_drag(self, event):
        self.canvas.coords(
            self.rect,
            self.start_x, self.start_y,
            event.x, event.y
        )

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        real_x1 = self.scale(x1)
        real_y1 = self.scale(y1)
        real_x2 = self.scale(x2)
        real_y2 = self.scale(y2)

        cropped = self.original_image.crop(
            (real_x1, real_y1, real_x2, real_y2)
        )

        self.show_preview(cropped, (real_x1, real_y1, real_x2, real_y2))
    
    def show_preview(self, cropped_img:Image, coords:tuple):
        preview = tk.Toplevel(self.root)
        preview.title("Confirm selection")

        preview.transient(self.root)
        preview.grab_set()

        coord_label = tk.Label(preview, text=f"Coords: {coords}")
        coord_label.pack()

        img_text = self.ocr.extract_text(cropped_img) or "[NO TEXT DETECTED]"
        # img_text_label = tk.Label(
        #     preview,
        #     text=img_text,
        #     wraplength=400,
        #     justify="left",
        # )
        # img_text_label.pack()
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        self.text_widget = tk.Text(
            preview,
            wrap="word",
            width=60,
            height=4,
            font=default_font
        )
        self.text_widget.insert("1.0", img_text)
        self.text_widget.pack()

        bold_btn = tk.Button(
            preview,
            text="Bold selection",
            command=self.bold_selection
        )
        bold_btn.pack()

        preview_img = ImageTk.PhotoImage(cropped_img)
        img_label = tk.Label(preview, image=preview_img)
        img_label.image = preview_img
        img_label.pack()

        accept_btn = tk.Button(
            preview,
            text="Accept",
            command=lambda: self.accept_crop(preview, cropped_img, img_text)
        )
        accept_btn.pack(side="left", padx=10, pady=10)

        retry_btn = tk.Button(
            preview,
            text="Retry",
            command=lambda: self.retry_selection(preview)
        )

        retry_btn.pack(side="right", padx=10, pady=10)
        preview.wait_window()

    def bold_selection(self):
        try:
            start = self.text_widget.index("sel.first")
            end = self.text_widget.index("sel.last")

            selected_text = self.text_widget.get(start, end)

            self.text_widget.delete(start, end)
            self.text_widget.insert(start, f"<b>{selected_text}</b>")

        except tk.TclError:
            print("No text selected")
    
    def accept_crop(self, preview_window, cropped_img, img_text):
        output_folder = Path("output") / str(self.today)
        output_folder.mkdir(parents=True, exist_ok=True)

        stem = self.current_path.stem
        suffix = self.current_path.suffix

        display_name = f"{stem}_display{suffix}"
        display_destination = output_folder / display_name
        self.display_image.save(display_destination)
        anki_destination = Path(self.config.anki_img_folder) / display_name
        shutil.copy2(display_destination, anki_destination)

        # cropped_name = f"{stem}_cropped{suffix}"
        # cropped_destination = output_folder / cropped_name
        # cropped_img.save(cropped_destination)

        audio_filename = f"{stem}_audio.mp3"
        audio_path = Path(self.config.anki_img_folder) / audio_filename
        self.tts.generate_audio_sync(self.text_widget.get("1.0", "end-1c"), audio_path)

        self.csv.append_to_csv(
            output_folder,
            self.text_widget.get("1.0", "end-1c"),
            display_name,
            audio_filename,
        )

        preview_window.destroy()
        self.next_image()
    
    def retry_selection(self, preview_window):
        preview_window.destroy()

        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None