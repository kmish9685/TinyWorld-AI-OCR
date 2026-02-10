"""
Premium UI Styling Module
Provides glassmorphism effects, hover animations, and visual enhancements for Tkinter
"""

import tkinter as tk

class PremiumButton(tk.Button):
    """
    Enhanced button with hover effects and premium styling
    """
    def __init__(self, parent, **kwargs):
        # Extract custom parameters
        self.base_bg = kwargs.pop('base_bg', '#6366F1')
        self.hover_bg = kwargs.pop('hover_bg', '#4F46E5')
        self.active_bg = kwargs.pop('active_bg', '#3730A3')
        
        # Initialize button
        super().__init__(parent, **kwargs)
        
        # Set initial background
        self.config(bg=self.base_bg)
        
        # Bind hover events
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
    
    def _on_hover(self, event):
        """Smooth hover effect"""
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        """Return to base color"""
        self.config(bg=self.base_bg)
    
    def _on_press(self, event):
        """Click press effect"""
        self.config(bg=self.active_bg)
    
    def _on_release(self, event):
        """Return to hover color"""
        self.config(bg=self.hover_bg)


class GlassPanel(tk.Frame):
    """
    Glassmorphism panel with enhanced borders and shadows
    """
    def __init__(self, parent, **kwargs):
        # Extract custom parameters
        glass_bg = kwargs.pop('glass_bg', '#1E1E3F')
        border_color = kwargs.pop('border_color', '#2D2D5F')
        border_width = kwargs.pop('border_width', 2)
        
        # Initialize frame
        super().__init__(parent, bg=glass_bg, **kwargs)
        
        # Add border effect
        self.config(
            highlightbackground=border_color,
            highlightthickness=border_width,
            relief='flat',
            bd=0
        )


def create_gradient_label(parent, text, font_size=14, bg_start='#6366F1', bg_end='#8B5CF6'):
    """
    Create a label with gradient-like effect (simulated with single color)
    Tkinter doesn't support true gradients, so we use a middle color
    """
    # Calculate middle color (simple average)
    frame = tk.Frame(parent, bg=bg_start, bd=0, relief='flat')
    label = tk.Label(frame, text=text, font=('Segoe UI', font_size, 'bold'),
                    bg=bg_start, fg='white', padx=20, pady=12)
    label.pack()
    return frame


def add_shadow_effect(widget, shadow_color='#00000030'):
    """
    Simulate shadow effect using borders
    """
    widget.config(
        highlightbackground=shadow_color,
        highlightthickness=3,
        bd=0
    )


def create_divider(parent, color='#374151', height=1, pady=15):
    """
    Create a subtle divider line
    """
    divider = tk.Frame(parent, height=height, bg=color)
    divider.pack(fill='x', pady=pady, padx=25)
    return divider
