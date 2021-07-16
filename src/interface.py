# Copyright 2021 iiPython

# Modules
import os
import re
import shutil
import subprocess
from rich.text import Text
from rich.panel import Panel
from iikp import readchar, keys
from rich import print as rich_print

# UI class
class TextWindow(object):
    def __init__(self, text: str, title: str) -> None:
        self.text = text
        self.title = title

        # Construct lines
        self.lines = text.split("\n")
        self.lineno = 0
        if not self.lines[-1].strip():
            self.lines = self.lines[:-1]

        # Attributes
        self._rich_regex = "\\[.[a-z]{2,}]"
        self._cls_cmd = "clear" if os.name != "nt" else "cls"

    def _ret_print(self, text: str) -> None:
        spc = " " * (shutil.get_terminal_size()[0] - 1)
        print(f"\r{spc}\r{text}", end = "")

    def clear(self) -> None:
        subprocess.run([self._cls_cmd], shell = True)

    def show(self) -> str:

        # Collect the terminal size
        rows = shutil.get_terminal_size()[1] - 4
        self.clear()

        # Info check
        lines = self.lines[self.lineno:]

        # Construct visible lines
        lineidx = 0
        visible = ""
        for line in lines:

            # Check index
            if lineidx == rows:
                break

            # Handle appending
            visible += line + "\n"
            lineidx += 1

        before = self.text.split(visible)[0] if visible else ""
        append = ""
        if before:
            append = "".join(_ for _ in re.findall(self._rich_regex, before))

        visible = append + visible[:-1]
        if len(visible.split("\n")) < rows:
            visible += "\n" * (rows - len(visible.split("\n")))

        # Handle printing
        rich_print(Panel(visible, title = self.title))
        print("CTRL+C to exit | R to refresh")

        return visible

    def display(self) -> bool:
        visible = self.show()
        while True:

            # Handle keypresses
            key = readchar()
            if key == keys.DOWN:

                # Logic check
                if visible.split("\n")[-1] == self.lines[-1]:
                    continue

                # Line handler
                self.lineno += 1
                if self.lineno == len(self.lines):
                    self.lineno = len(self.lines) - 1

            elif key == keys.UP:
                self.lineno -= 1
                if self.lineno < 0:
                    self.lineno = 0

            elif key == keys.CTRL_C:
                self.clear()
                return False

            elif key == "r":
                self.clear()
                return True

            visible = self.show()
