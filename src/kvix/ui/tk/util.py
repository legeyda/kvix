from tkinter import Misc
from typing import Generator


def find_all_children(root: Misc) -> Generator[Misc, Misc, None]:
    yield root
    for item in root.winfo_children():
        yield from find_all_children(item)
