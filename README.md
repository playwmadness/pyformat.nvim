# pyformat.nvim

A combination of black and isort python formatters for Neovim.

## Installation

### Prerequisites

- If you're not using venv, I would recommend creating one
```bash
mkdir -p ~/.local/venv && cd ~/.local/venv
python3 -m venv nvim
nvim/bin/pip install -U pynvim black isort
```
- Then in your init.lua
```lua
vim.g.python3_host_prog = vim.env.HOME .. '/.local/venv/nvim/bin/python'
```

### Plugin manager

lazy.nvim:
```lua
{
  'playwmadness/pyformat.nvim',
  build = { ':UpdateRemotePlugins' },
  ft = { 'python' },
}
```

## Usage

Call `:PyFormat` to format current buffer.

Alternatively there is synchronous `:PyFormatSync` which can be used with autocmd like 
```vim
au BufWritePre *.py,*.pyi PyFormatSync
```
to format your python files before writing them

## Configuration

Defaults:
```lua
vim.g['pyformat#black#settings'] = {
    line_length = 88,
    fast = false,
}
```
