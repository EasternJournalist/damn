#!/usr/bin/python3
import sys
import os
import requests
import json
from typing import *
import argparse


API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

MODEL_ID = 'doubao-1-5-pro-32k-250115'

PROMPT_INSTRUCT = """
You are a Linux command assistant.
Respond to the user's natural language instruction with the exact Linux command in one single line.
Your response must contain only the command, with no explanations, comments, or extra text.
If required information is missing, use clear placeholders in angle brackets (e.g., <filename> or <directory>).
Do not include shell prompts ($) or line breaks.
Reply with only the command.
"""

PROMPT_FIX = """
You are a Linux command repair assistant.
The user will input a possibly incorrect or incomplete Linux command.
Your task is to correct it and respond with the corrected command in one single line.
Do not include any explanations, comments, or additional text.
Do not include shell prompts ($) or line breaks.
If necessary, use clear placeholders (e.g., <filename>, <command>, <path>).
Output only the corrected command.
"""


def bind():
    bashrc = os.path.expanduser("~/.bashrc")
    bind_snippet = \
r'''
# === damn bind ===

# Unique output file per terminal
export DAMN_OUT_FILE="/tmp/damn_out_$(tty | tr '/' '_')"

# Register cleanup on shell exit
_cleanup_damn_out_file() {
    [ -f "$DAMN_OUT_FILE" ] && rm -f "$DAMN_OUT_FILE"
}
trap _cleanup_damn_out_file EXIT

# Main damn function (Alt+D triggers it)
damn_ai_key() {
    local prompt_str=$(eval "printf \"%s\" \"\${PS1@P}\"")
    local prompt_len=${#prompt_str}
    local user_input="$READLINE_LINE"
    local damn_bin=$HOME/.local/bin/damn

    printf "%s" "$prompt_str" >&2
    printf "\033[90m%s\033[0m\n" "$user_input" >&2

    printf "%s" "$prompt_str" >&2
    printf "\033[90m" >&2
    printf "🤔\b\b" >&2
    if [[ -z "$user_input" || "$user_input" =~ ^[[:space:]]*$ ]]; then
        local last_cmd
        last_cmd=$(fc -ln -0)
        printf "%s\n" "$last_cmd" >&2
        $damn_bin -i "$last_cmd" -m fix | tee "$DAMN_OUT_FILE"
    else
        $damn_bin -i "$user_input" -m instruct | tee "$DAMN_OUT_FILE"
    fi
    printf "\033[0m" >&2

    local new_cmd=$(tail -n 1 "$DAMN_OUT_FILE")
    printf "\033[2K\r" >&2
    READLINE_LINE="$new_cmd"
    READLINE_POINT=${#READLINE_LINE}
}

bind -x '"\ed":damn_ai_key'

# === end damn bind ===
'''

    with open(bashrc, 'a') as f:
        f.write(bind_snippet)


def unbind():
    bashrc = os.path.expanduser("~/.bashrc")
    with open(bashrc, 'r') as f:
        lines = f.readlines()
    try:
        start_line = next(i for i, line in enumerate(lines) if line.startswith("# === damn bind ==="))
        end_line = next(i for i, line in enumerate(lines) if line.startswith("# === end damn bind ==="))
        lines = lines[:start_line] + lines[end_line+1:]
        with open(bashrc, 'w') as f:
            f.write("".join(lines))
    except StopIteration:
        pass


def init():
    unbind()
    bind()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Command line interface for damn")
    parser.add_argument(
        "-i", "--input",
        dest="user_input",
        type=str,
        required=False,
        help="Input command or instruction"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["instruct", "fix"],
        default="instruct",
        help="Mode of operation"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize damn",
    )   
    args = parser.parse_args()
    
    user_input: str = args.user_input
    mode: Literal['instruct', 'fix'] = args.mode

    # Init bashrc
    if args.init:
        init()
        return
    
    # Check API key
    if 'ARK_API_KEY' not in os.environ:
        print("Please set ARK_API_KEY environment variable")
    api_key = os.environ.get("ARK_API_KEY")

    # Run
    system_prompt = PROMPT_INSTRUCT if mode == "instruct" else PROMPT_FIX

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "model": MODEL_ID,
        "stream": True
    }

    response_text = ""
    with requests.post(API_URL, headers=headers, data=json.dumps(data), stream=True) as resp:
        for line in resp.iter_lines(decode_unicode=True):
            if line.startswith("data:"):
                line = line[5:].strip()
            else:
                continue
            if line == "[DONE]":
                break
            chunk = json.loads(line)
            delta = chunk["choices"][0]["delta"].get("content", "")
            if delta:
                print(delta, end='', flush=True)
                response_text += delta

if __name__ == '__main__':
    main()