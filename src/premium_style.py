"""
Premium Apple-inspired UI styling module.
Provides glassmorphism effects and smooth animations for Tkinter.
"""
import tkinter as tk

class PremiumStyle:
    """Apple-inspired design system"""
    
    # iOS Color Palette
    COLORS = {
        'ios_blue': '#007AFF',
        'ios_green': '#34C759',
        'ios_purple': '#5E5CE6',
        'ios_red': '#FF3B30',
        'background_start': '#F5F7FA',
        'background_end': '#E8EAF6',
        'card_bg': '#FFFFFF',
        'card_glass': '#F8F9FA',  # Simulated frosted glass
        'text_primary': '#1D1D1F',
        'text_secondary': '#86868B',
        'border_light': '#E5E7EB',
        'shadow': '#00000015',
    }
    
    # Typography (SF Pro inspired)
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 13, 'bold'),
        'body': ('Segoe UI', 11),
        'caption': ('Segoe UI', 9),
        'mono': ('Consolas', 10),
    }
    
    # Spacing (8px grid)
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 24,
        'xxl': 32,
    }
    
    # Border Radius
    RADIUS = {
        'sm': 8,
        'md': 12,
        'lg': 16,
        'pill': 999,
    }
    
    @staticmethod
    def create_glass_frame(parent, **kwargs):
        """Create a glassmorphism-style frame"""
        return tk.Frame(
            parent,
            bg=PremiumStyle.COLORS['card_glass'],
            highlightbackground=PremiumStyle.COLORS['border_light'],
            highlightthickness=1,
            **kwargs
        )
    
    @staticmethod
    def create_premium_button(parent, text, style='primary', **kwargs):
        """Create a premium iOS-style button"""
        colors = {
            'primary': (PremiumStyle.COLORS['ios_blue'], 'white'),
            'success': (PremiumStyle.COLORS['ios_green'], 'white'),
            'secondary': (PremiumStyle.COLORS['card_glass'], PremiumStyle.COLORS['text_primary']),
        }
        
        bg, fg = colors.get(style, colors['primary'])
        
        return tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=PremiumStyle.FONTS['body'],
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=PremiumStyle.SPACING['lg'],
            pady=PremiumStyle.SPACING['sm'],
            **kwargs
        )
