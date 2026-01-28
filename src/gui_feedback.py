"""
GUI feedback module using tkinter.
Provides visual feedback during recording, processing, and error states.
"""

import logging
import tkinter as tk
from tkinter import font

logger = logging.getLogger(__name__)


class FeedbackWindow(tk.Tk):
    """Borderless, always-on-top tkinter window for feedback display."""
    
    def __init__(self):
        """Initialize feedback window."""
        super().__init__()
        
        # Window configuration
        self.title("Whisper Dictation")
        self.geometry("200x100")
        self.overrideredirect(True)  # Borderless
        self.attributes("-topmost", True)  # Always on top
        self.attributes("-alpha", 0.9)  # Slight transparency
        
        # Center window on screen
        self._center_window()
        
        # Configure style
        self.config(bg="#1e1e1e")
        
        # Create main frame
        main_frame = tk.Frame(self, bg="#1e1e1e")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Create label for emoji and text
        label_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.label = tk.Label(
            main_frame,
            text="",
            font=label_font,
            bg="#1e1e1e",
            fg="#00ff00",
            wraplength=180
        )
        self.label.pack(expand=True, fill=tk.BOTH)
        
        # Create close button
        button_frame = tk.Frame(main_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        close_btn = tk.Button(
            button_frame,
            text="Fermer (Q)",
            font=("Segoe UI", 9),
            bg="#333333",
            fg="#cccccc",
            bd=0,
            padx=5,
            pady=2,
            command=self._on_close_btn,
            relief=tk.RAISED
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Bind keyboard shortcuts
        self.bind("<q>", lambda e: self._on_close_btn())
        self.bind("<Escape>", lambda e: self._on_close_btn())
        
        # State tracking
        self._current_state = None
        self._error_timer = None
        self._close_callback = None
        self.withdraw()  # Hidden by default
        
        logger.info("FeedbackWindow initialized")
    
    def _center_window(self):
        """Center window on screen."""
        self.update_idletasks()
        width = 200
        height = 80
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_listening(self):
        """Show listening state (thread-safe)."""
        self.after(0, self._show_listening_impl)

    def _show_listening_impl(self):
        """Internal implementation of show_listening."""
        self._cancel_error_timer()
        self._current_state = "listening"
        self.label.config(text="🎤 Écoute...", fg="#00ff00")
        self.deiconify()
        logger.debug("Showing listening state")
    
    def show_processing(self):
        """Show processing state (thread-safe)."""
        self.after(0, self._show_processing_impl)

    def _show_processing_impl(self):
        """Internal implementation of show_processing."""
        self._cancel_error_timer()
        self._current_state = "processing"
        self.label.config(text="⏳ Traitement...", fg="#ffaa00")
        self.deiconify()
        logger.debug("Showing processing state")
    
    def show_downloading(self, progress_percent):
        """Show model download progress (thread-safe)."""
        self.after(0, lambda: self._show_downloading_impl(progress_percent))

    def _show_downloading_impl(self, progress_percent):
        """Internal implementation of show_downloading."""
        self._cancel_error_timer()
        self._current_state = "downloading"
        self.label.config(text=f"📥 Téléchargement...\n{progress_percent}%", fg="#00aaff")
        self.deiconify()
        logger.debug(f"Showing download progress: {progress_percent}%")
    
    def show_error(self, message, duration_ms=3000):
        """Show error message (thread-safe)."""
        self.after(0, lambda: self._show_error_impl(message, duration_ms))

    def _show_error_impl(self, message, duration_ms):
        """Internal implementation of show_error."""
        self._cancel_error_timer()
        self._current_state = "error"
        self.label.config(text=f"❌ {message}", fg="#ff0000")
        self.deiconify()
        logger.debug(f"Showing error: {message}")
        
        # Auto-hide after duration
        self._error_timer = self.after(duration_ms, self.hide)
    
    def hide(self):
        """Hide the window (thread-safe)."""
        self.after(0, self._hide_impl)

    def _hide_impl(self):
        """Internal implementation of hide."""
        self._cancel_error_timer()
        self._current_state = None
        self.withdraw()
        logger.debug("Hiding window")
    
    def _cancel_error_timer(self):
        """Cancel pending error auto-hide timer if any."""
        if self._error_timer is not None:
            self.after_cancel(self._error_timer)
            self._error_timer = None
    
    def set_close_callback(self, callback):
        """Set callback to call when close is requested."""
        self._close_callback = callback
    
    def _on_close_btn(self):
        """Handle close button or escape key."""
        logger.info("Close requested")
        if self._close_callback:
            self._close_callback()
        else:
            # Fallback: quit directly
            self.quit()
