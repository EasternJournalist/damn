#!/usr/bin/python3
import sys
import os
import requests
import json
from typing import *
import argparse


# Acturally, any API compatible with OpenAI is supported.
# Add more API configs here if needed.
API_CONFIGS = {
    "OpenAI GPT": {
        "api_url": "https://api.openai.com//v1/chat/completions",
        "model_id": "gpt-4o-mini",
        "api_key_name": "OPENAI_API_KEY"
    },
    "Google Gemini": {
        "api_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model_id": "gemini-2.5-flash-preview-05-20",
        "api_key_name": "GEMINI_API_KEY"
    },
    "ByteDance Doubao": {
        "api_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "model_id": "doubao-1-5-pro-32k-250115",
        "api_key_name": "DOUBAO_API_KEY"
    }
}


API_SERVICE_NAME = os.environ.get("DAMN_API_SERVICE_NAME", "Google Gemini")

if API_SERVICE_NAME in API_CONFIGS:
    API_URL = API_CONFIGS[API_SERVICE_NAME]["api_url"]
    API_KEY = os.environ.get(API_CONFIGS[API_SERVICE_NAME]["api_key_name"])
    MODEL_ID = API_CONFIGS[API_SERVICE_NAME]["model_id"]
elif API_SERVICE_NAME == "Custom":
    API_URL = os.environ.get("DAMN_API_URL")
    API_KEY = os.environ.get("DAMN_API_KEY")
    MODEL_ID = os.environ.get("DAMN_MODEL_ID")
else:
    print(f"\033[91mInvalid API service name: {API_SERVICE_NAME}. Please choose from {list(API_CONFIGS.keys())} or Custom.\033[0m")


def get_linux_distribution():
    info = {}
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    info[key] = val.strip('"')
    except FileNotFoundError:
        pass
    return info

linux_distro = get_linux_distribution()
linux_distro_name = linux_distro.get('PRETTY_NAME', None)

def bind():
    global API_SERVICE_NAME
    bashrc = os.path.expanduser("~/.bashrc")
    
    print(f"👉 Choose an API service for damn:")
    for i, (name, config) in enumerate(API_CONFIGS.items()):
        print(f"    [{i + 1}] {name}")
    while True:
        choice = input("Enter a number: ")
        try:
            choice = int(choice)
            if choice < 1 or choice > len(API_CONFIGS):
                raise ValueError()
            API_SERVICE_NAME = list(API_CONFIGS.keys())[choice - 1]
            break
        except (ValueError, IndexError):
            print(f"❌ Invalid choice. Please enter a number between 1 and {len(API_CONFIGS)}.")
    print(f"✅ API service set to \033[1m{API_SERVICE_NAME}\033[0m.")
    api_key_name = API_CONFIGS[API_SERVICE_NAME]["api_key_name"]
    API_KEY = os.environ.get(api_key_name)
    # yellow highlight is \033[93m, reset is \033[0m
    # red highlight is \033[91m, reset is \033[0m
    # red bold is \033[1;91m, reset is \033[0m
    set_env_var_snippet = ""
    if API_KEY is None:
        print("❗ The API key environment variable is not set. You might need to get one from the API provider.")
        print("   Get one and enter it here, the environment variable will be set.")
        try:
            API_KEY = input(f"Enter {api_key_name} value (or press Ctrl+C to skip): ")
            set_env_var_snippet = f"export {api_key_name}=\"{API_KEY}\""
        except KeyboardInterrupt:
            print()
            print(f"❗ Please set the environment variable \033[1m{api_key_name}\033[0m later.")
    else:
        print(f"✅ {api_key_name} environment variable is found.")
    bind_snippet = \
f'''
{set_env_var_snippet}
''' \
r'''
# === damn bind ===

# Unique output file per terminal
export DAMN_OUT_FILE="/tmp/damn_out_$(tty | tr '/' '_')"
'''\
f'''
export DAMN_API_SERVICE_NAME="{API_SERVICE_NAME}"
''' \
r'''
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
    
    print("✅ damn configured in ~/.bashrc.")


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


def init_config():
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
        "--config",
        action="store_true",
        help="Initialize damn",
    )   
    args = parser.parse_args()
    
    user_input: str = args.user_input
    mode: Literal['instruct', 'fix'] = args.mode

    # Init bashrc
    if args.config:
        init_config()
        return

    # Run
    if API_KEY is None:
        print(f"\033[91mAPI key is not set. Please set the environment variable {API_CONFIGS[API_SERVICE_NAME]['api_key_varname']} for {API_SERVICE_NAME}\033[0m")
        return

    PROMPT_MESSAGES_INSTRUCT = [
        {
            "role": "system", 
            "content": f"You are a Linux command assistant. {f'({linux_distro_name})' if linux_distro_name else ''}"\
                "Respond to the user's natural language instruction with the exact Linux command in one single line. "\
                "Your response must contain only the command, with no explanations, comments, or extra text. "\
                "If required information is missing, use clear placeholders in angle brackets (e.g., <filename> or <directory>). "\
                "Reply with only the command. "
        },
        {"role": "user", "content": "list files"},
        {"role": "assistant", "content": "ls"},
    ]

    PROMPT_MESSAGES_FIX = [
        {
            "role": "system",
            "content": f"You are a Linux command assistant. {f'({linux_distro_name})' if linux_distro_name else ''}"\
                "The user will input a possibly incorrect or incomplete Linux command. "\
                "Your task is to correct it and respond with the corrected command in one single line. "\
                "Do not include any explanations, comments, or additional text. "\
                "If necessary, use clear placeholders (e.g., <filename> or <directory>). "\
                "Output only the corrected command. "
        },
        {"role": "user", "content": "nvidai-smi"},
        {"role": "assistant", "content": "nvidia-smi"},
    ]

    prompt_messages = PROMPT_MESSAGES_INSTRUCT if mode == "instruct" else PROMPT_MESSAGES_FIX

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "messages": [
            *prompt_messages,
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