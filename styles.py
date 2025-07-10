import tkinter as tk
from tkinter import ttk

def apply_styles(widget_type, **kwargs):
    styles = {
        "entry": {
            "font": ("Segoe UI", 10),
            "foreground": "#333333",
            "background": "#ffffff",
            "borderwidth": 1,
            "relief": "solid"
        },
        
        "button": {
            "style": "Accent.TButton",
            "width": 25,
            "padding": 10
        },
        "label": {
            "style": "TLabel",
            "font": ("Segoe UI", 14),
            "foreground": "#333333"
        },
        "text": {
            "width": 50,
            "height": 15,
            "font": ("Consolas", 10),
            "background": "#ffffff",
            "foreground": "#333333",
            "insertbackground": "#333333",
            "selectbackground": "#0078d7",
            "borderwidth": 1,
            "relief": "solid"
        },
        "frame": {
            "style": "TFrame"
        },
        "canvas": {
            "background": "#ffffff",
            "highlightthickness": 0,
            "borderwidth": 0
        }

    }
    style = styles.get(widget_type, {})
    style.update(kwargs)
    return style

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar estilo do Frame
    style.configure('TFrame', background="#f5f5f5")
    
    # Configurações gerais
    style.configure('.', background="#f5f5f5", foreground="#333333")
    
    # Botão padrão
    style.configure('TButton',
                   font=("Segoe UI", 11),
                   padding=8,
                   relief="flat",
                   background="#e1e1e1",
                   foreground="#333333")
    style.map('TButton',
              background=[('active', '#d5d5d5')])
    
    # Botão de destaque
    style.configure('Accent.TButton',
                    font=("Segoe UI Semibold", 11),
                    foreground="white",
                    background="#0078d7")
    style.map('Accent.TButton',
              background=[('active', '#006cbe')])
    
    # Frame de autenticação
    style.configure('Auth.TFrame',
                   background="#ffffff",
                   borderwidth=1,
                   relief="solid")
    style.configure('Danger.TButton',
                  foreground="white",
                  background="#dc3545")
     
    style.map('Danger.TButton',
              background=[('active', '#c82333')])

def create_button(parent, text, command, **kwargs):
    return ttk.Button(parent, text=text, command=command, **apply_styles("button", **kwargs))

def create_label(parent, text, **kwargs):
    return ttk.Label(parent, text=text, **apply_styles("label", **kwargs))

def create_text(parent, **kwargs):
    return tk.Text(parent, **apply_styles("text", **kwargs))

def create_frame(parent, **kwargs):
    return ttk.Frame(parent, **apply_styles("frame", **kwargs))

def create_canvas(parent, **kwargs):
    return tk.Canvas(parent, **apply_styles("canvas", **kwargs))