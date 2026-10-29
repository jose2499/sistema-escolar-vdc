import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import tkinter as tk
from escolar.presentation.login_view import LoginView


def main():
    root = tk.Tk()
    root.eval("tk::PlaceWindow . center")
    app = LoginView(root)
    root.mainloop()


if __name__ == "__main__":
    main()

