import tkinter as tk

from escolar.presentation.login_view import LoginView


def main():
    root = tk.Tk()
    root.eval("tk::PlaceWindow . center")
    LoginView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
