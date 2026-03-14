import tkinter as tk
import json
from datetime import datetime

from StudyTrakerApp import StudyTrakerApp

TAREAS= "tareas.json"

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTrakerApp(root)
    root.mainloop()
    
            