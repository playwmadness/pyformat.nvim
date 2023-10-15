import sys
from typing import Union

import pynvim

try:
    import black
    import isort
    from black.parsing import InvalidInput
    from black.report import NothingChanged
except ImportError:
    # TODO: ImportError
    sys.exit(1)


@pynvim.plugin
class PyformatNvim:
    def __init__(self, nvim: pynvim.Nvim):
        self.nvim = nvim

    def black_opts(self) -> dict[str, Union[int, bool]]:
        # TODO:
        options = {
            "fast": False,
            "is_pyi": self.nvim.current.buffer.name.endswith(".pyi"),
        }
        user_options = self.nvim.vars.get("pyformat#black#settings")
        if user_options:
            options.update(user_options)
        return options

    def isort_opts(self) -> dict[str, Union[int, bool]]:
        # TODO:
        options = {}
        user_options = self.nvim.vars.get("pyformat#isort#settings")
        if user_options:
            options.update(user_options)
        return options

    @pynvim.command(
        "PyFormat",
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
        buf = "\n".join(self.nvim.current.buffer[range[0] - 1 : range[1]])

        opts = self.isort_opts()
        buf = isort.code(buf)

        opts = self.black_opts()
        mode = black.Mode(
            is_pyi=opts["is_pyi"],
        )

        try:
            buf = black.format_file_contents(
                buf,
                fast=opts["fast"],
                mode=mode,
            )
        except NothingChanged:
            return
        except InvalidInput:
            return

        cursor = self.nvim.current.window.cursor
        self.nvim.current.buffer[range[0] - 1 : range[1]] = buf.split("\n")[:-1]
        try:
            self.nvim.current.window.cursor = cursor
        except pynvim.NvimError:
            self.nvim.current.window.cursor = (len(self.nvim.current.buffer), 0)
