# Huggingface Downloader

This is a simple script to download the models from [Huggingface](https://huggingface.co/) and save them in a folder.

## Installation

1. Clone this repo.
2. Install the repo with `pip install -e .`

## Usage

```
usage: hfdown [-h] --repo REPO [--branch BRANCH] (--dir DIR | --base-dir BASE_DIR) [--force] [--skip-safetensor]

optional arguments:
  -h, --help           show this help message and exit
  --repo REPO          Name of Huggingface repo. e.g. THUDM/chatglm3-6b
  --branch BRANCH      Branch to download. Default: main
  --dir DIR            Directory to save the files.
  --base-dir BASE_DIR  Base directory to save the files. The files will be saved to <base-dir>/<repo>.
  --force              Force download even if the file already exists.
  --skip-safetensor    Skip safetensor files.
```

> Note that `--dir` and `--base-dir` are mutually exclusive.

Example:

```bash
hfdown --repo THUDM/chatglm3-6b --base-dir ~/models --skip-safetensor
```