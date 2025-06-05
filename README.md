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

You will need an API key from https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey (ByteDance).  
Free credits are enough for one year of usage.

Then add it to your `~/.bashrc` file as an environment variable:

```
echo "export ARK_API_KEY=YOUR_API_KEY" >> ~/.bashrc; source ~/.bashrc
```

## Similar to
- [thefuck](https://github.com/nvbn/thefuck), but with AI.
- [shell_gpt](https://github.com/TheR1D/shell_gpt), but easier and only for command.