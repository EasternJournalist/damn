# Just give me the damn command

> **I don’t speak bash.**  
> **But I know what I want.**
>
> **Just press Alt+D —**  
> **and get the damn command.**

<img width=100% src=https://github.com/user-attachments/assets/a7c9a0a6-1865-4748-9f1e-782965a81075>

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/EasternJournalist/damn/refs/heads/master/install.sh | bash; source ~/.bashrc
```


### Get an API Key

You will need an API key to use th AI models. Choose one of the following APIs and click the link to get an API key:

| API Service | Default Model | Environment Variable Name |
| --- | --- | --- |
| [OpenAI GPT](https://platform.openai.com/api-keys) |  gpt-4o-mini |  `OPENAI_API_KEY` |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/api-key) | gemini-2.5-flash-preview-05-20 | `GEMINI_API_KEY` |
| [ByteDance Doubao](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) | doubao-1-5-pro-32k-250115 | `DOUBAO_API_KEY` |

***Generally, free credits are quite sufficient for using damn daily.***

Then you can add the key to your `~/.bashrc` file as an user environment variable, for example:

```
echo "export OPENAI_API_KEY=XXXX-XXXX-XXXX" >> ~/.bashrc; source ~/.bashrc
```

## Similar to
- [thefuck](https://github.com/nvbn/thefuck), but with AI.
- [shell_gpt](https://github.com/TheR1D/shell_gpt), but easier and only for command.