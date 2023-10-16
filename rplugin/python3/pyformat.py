import sys
from io import StringIO
from typing import Union

import pynvim

import_error = False

try:
    import isort
except ImportError:
    import_error = True
    print(
        "isort is not installed in your g:python3_host_prog",
        file=sys.stderr,
    )

try:
    import black
    from black.const import DEFAULT_LINE_LENGTH
    from black.parsing import InvalidInput
    from black.report import NothingChanged
except ImportError:
    import_error = True
    print(
        "black is not installed in your g:python3_host_prog",
        file=sys.stderr,
    )

if import_error:
    print(
        "Make sure all required dependencies are installed and try again",
        file=sys.stderr,
    )
    sys.exit(1)


@pynvim.plugin
class PyformatNvim:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    def black_opts(self) -> dict[str, Union[int, bool]]:
        options = {
            "line_length": DEFAULT_LINE_LENGTH,
            "fast": False,
            "is_pyi": self.nvim.current.buffer.name.endswith(".pyi"),
        }
        user_options = self.nvim.vars.get("pyformat#black#settings")
        if user_options:
            options.update(user_options)
        return options

    def isort_opts(self) -> dict[str, Union[int, bool]]:
        options = {
            "is_pyi": self.nvim.current.buffer.name.endswith(".pyi"),
        }
        user_options = self.nvim.vars.get("pyformat#isort#settings")
        if user_options:
            options.update(user_options)
        return options

    @pynvim.command(
        "PyFormatSync",
        range="%",
        sync=True,
    )
    def format_sync(self, range):
        return self.format(range)

    @pynvim.command(
        "PyFormat",
        range="%",
    )
    def format(self, range):
        if self.nvim.current.buffer.options.get("filetype") != "python":
            self.nvim.err_write("Buffer filetype is not python\n")
            return

        buf = "\n".join(self.nvim.current.buffer[range[0] - 1 : range[1]])

        opts = self.isort_opts()
        isort_in = StringIO(buf)
        isort_out = StringIO()
        isorted = isort.api.sort_stream(
            isort_in,
            isort_out,
            extension="pyi" if opts["is_pyi"] else "py",
        )
        if isorted:
            isort_out.seek(0)
            buf = isort_out.read()

        opts = self.black_opts()
        mode = black.Mode(
            line_length=opts["line_length"],
            is_pyi=opts["is_pyi"],
        )

        try:
            buf = black.format_file_contents(buf, fast=opts["fast"], mode=mode)
        except NothingChanged:
            if not isorted:
                self.nvim.out_write("Nothing changed\n")
                return
        except InvalidInput:
            self.nvim.err_write("black: Invalid input\n")
            return

        cursor = self.nvim.current.window.cursor
        self.nvim.current.buffer[range[0] - 1 : range[1]] = buf.split("\n")[:-1]
        try:
            self.nvim.current.window.cursor = cursor
        except pynvim.NvimError:
            self.nvim.current.window.cursor = (len(self.nvim.current.buffer), 0)
