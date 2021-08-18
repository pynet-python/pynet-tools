# Copyright 2021 iiPython

# Modules
import os
import sys
import rich
import shutil
import zipfile
from rich import print
from iikp import readchar
from types import FunctionType
from rich.console import Console
from src.interface import TextWindow

# Initialization
rcon = Console()
def close_script(code: int, message = None):
    print(str(message) if message is not None else "", end = "\n" if message is not None else "")
    sys.exit(code)

def format_multiline(text: str) -> str:
    return "".join(_.split("~")[1].lstrip(" ") + "\n" for _ in text.split("\n")[1:][:-1])[:-1]

# Handle options
sys.argv = sys.argv[1:]
if not sys.argv or sys.argv and sys.argv[0] == "help":
    message = format_multiline("""
    ~ [blue bold]DTP Project Packager
    ~ [yellow bold]============================================
    ~
    ~ [cyan]Basic syntax: [yellow]packager.py [blue]<option> [args][/blue]
    ~
    ~ [yellow]Available options:
    ~ [yellow]    help                  | shows this message
    ~ [yellow]    init                  | initializes the 'content' folder
    ~ [yellow]    purge                 | deletes all package content
    ~ [yellow]    pack                  | packages the 'content' directory
    ~ [yellow]    preview \\[path]        | previews the specified file
    ~ [yellow]    clean                 | cleans up packaging files
    ~
    ~ [bright_black]Copyright 2021 iiPython; MIT License
    """)
    close_script(0, message)

# Command handler
class Handler(object):
    def __init__(self) -> None:
        self.commands = []

    def command(self) -> FunctionType:
        def internal_callback(cb: FunctionType) -> None:
            self.commands.append(cb)

        return internal_callback

    def execute_all(self) -> any:
        for command in self.commands:
            if command.__name__ == sys.argv[0]:
                return command(sys.argv[1:])

        return close_script(1, f"[yellow]Unrecognized command: '{sys.argv[0]}'")

handler = Handler()

# Construct commands
@handler.command()
def init(args: list) -> None:
    if not os.path.isdir("content"):
        os.mkdir("content")
        close_script(0)

    else:
        close_script(1, "[red]Content already initialized, perhaps you meant 'purge'?")

@handler.command()
def purge(args: list) -> None:
    if not os.path.isdir("content"):
        close_script(1, "[red]It seems no content exists, ensure you ran 'packager.py init'.")

    print("[red bold]WARNING![/red bold] [yellow]This will delete [/yellow][red bold]ALL[/red bold][yellow] of your content.\nType 'YES' to confirm this action.[/yellow]")
    try:
        if input("> ") == "YES":
            try:
                shutil.rmtree("content")
                os.mkdir("content")

                close_script(0, "\n[green]Successfully purged content.")

            except Exception as Error:
                close_script(1, f"\n[red]Failed purging content: '{Error}'")

        else:
            close_script(-1)

    except KeyboardInterrupt:
        close_script(-1)

@handler.command()
def pack(args: list) -> None:
    if not os.path.isdir("content"):
        close_script(1, "[red]It seems no content exists, ensure you ran 'packager.py init'.")

    elif os.path.isfile("package.zip"):
        print("[yellow]Notice: package.zip already exists, press 'y' to overwrite it.")
        if readchar() == "y":
            os.remove("package.zip")

        else:
            close_script(-1, "Canceled packaging due to conflict package.")

    # Package files into zip
    with zipfile.ZipFile("package.zip", "w") as zip_file:
        for root, _, files in os.walk("content"):
            for file in files:
                zip_file.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file),
                        os.path.abspath("content")
                    )
                )

@handler.command()
def clean(args: list) -> None:
    if not os.path.isfile("package.zip"):
        close_script(0, "[yellow]Nothing to clean.")

    os.remove("package.zip")
    close_script(0, "OK")

@handler.command()
def preview(args: list) -> None:
    if not args:
        close_script(1, "[yellow]usage: preview <path>")

    elif len(args) > 1:
        close_script(1, "[yellow]You cannot preview multiple files.")

    # Calculate path
    fp = os.path.abspath(os.path.join("content", args[0]))
    if os.path.isdir(fp):
        close_script(1, "[red]You cannot preview directories.")

    elif not os.path.exists(fp):
        close_script(1, "[red]No such path exists (please note it should be relative to 'content').")

    # Check size
    if os.stat(fp).st_size > 20971520:
        close_script(1, "[red]The given file is larger than 20mb.")

    # Display loop
    while True:

        # Fetch text
        text = ""
        try:
            with open(fp, "rb") as raw:
                text = raw.read().decode("UTF-8")

        except UnicodeDecodeError:
            text = "<binary file>"

        # Show preview
        try:
            tw = TextWindow(text, args[0])

        except rich.errors.MarkupError as Error:
            tw = TextWindow(f"<Formatting Error>\n{Error}", args[0])

        if not tw.display():
            break

# Handle all
handler.execute_all()
