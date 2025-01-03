![banner.png](sample/banner.png)

# 🐱 neko-chan-telegram-bot

[![Docker Image CI](https://github.com/wiseCirno/neko-chan-telegram-bot/actions/workflows/docker-image.yml/badge.svg?branch=master)](https://github.com/wiseCirno/neko-chan-telegram-bot/actions/workflows/docker-image.yml)

neko is a self-hosted Telegram bot designed for acg lovers.

## 💡 Features

<div style="overflow-x: auto;">
  <table style="width: 100%; table-layout: fixed;">
    <tr>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/anime_search.png" alt="Anime Search" style="width: auto; height: auto; max-height: 600px;">
        <p>📺 Anime search</p>
      </td>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/chat.png" alt="Chat Anywhere" style="width: auto; height: auto; max-height: 600px;">
        <p>💬 In-APP ChatGPT</p>
      </td>
    </tr>
    <tr>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/sticker.png" alt="Stickers" style="width: auto; height: auto; max-height: 600px;">
        <p>😊 Get sticker & 🐉 "Long Sticker"</p>
      </td>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/image_search.png" alt="Image Reverse Search" style="width: auto; height: auto; max-height: 600px;">
        <p>🖼️ Image reverse search</p>
      </td>
    </tr>
    <tr>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/upload_epub.png" alt="Upload EPUB" style="width: auto; height: auto; max-height: 600px;">
        <p>📖 Pack Telegraph to Epub</p>
      </td>
    </tr>
  </table>
</div>
<div style="overflow-x: auto;">
  <table>
    <tr>
      <td style="text-align: center; width: 50%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
        <img src="sample/komga.png" alt="Sync Komga" style="width: auto; height: auto; max-height: 600px;">
        <p>💾 Sync manga from Telegraph</p>
      </td>
    </tr>
  </table>
</div>

## 🔧 Docker Deployment

### Get Image

You can pull the image from **darinirvana/neko-chan:latest** or manually build it
from [Dockerfile](https://github.com/Ziang-Liu/Neko-Chan/blob/master/Dockerfile).

### Environment Variables:

| Variable             | Description                                           | Default       |  
|----------------------|-------------------------------------------------------|---------------|  
| BOT_TOKEN            | (Required) You can not leave this                     | `None`        |  
| MY_USED_ID           | (Optional) Used for Telegraph sync service            | `-1`          |  
| CHAT_ANYWHERE_KEY    | (Optional) You can use your personal key              | `None`        |
| CHAT_ANYWHERE_MODEL  | (Optional) Choose the custom model                    | `gpt-4o-mini` |
| CHAT_ANYWHERE_PROMPT | (Optional) Customized for different purposes          | `TL;DR`       |
| CF_WORKER_PROXY      | (Optional) CloudFlare Workers proxy                   | `None`        |
| PROXY                | (Optional) For special network environment use        | `None`        |  
| TELEGRAPH_THREADS    | (Optional) Set this value too high is not recommended | `2`           |

### Additional Information

Mount `/path/to/your/localhost` to `/neko`.

## Bot Config

Below is a set of sample commands that can be added to your personal bot:

``` txt
hug - 抱抱 Neko！  
cuddle - 轻轻搂住 Neko
pet - 摸摸 Neko 的头
kiss - 亲亲 Neko 的脸颊  
snog - 抱住 Neko 猛亲 
anime - 通过一瞬截图搜索动漫
komga - 启用漫画下载服务  
chat - 和 Neko 交流！ 
bye - 关闭 chat
help - Neko 的使用方法  
```

## Acknowledgements

Epub generation based on [ebooklib](https://github.com/aerkalov/ebooklib)

Image search based on [PicImageSearch](https://github.com/kitUIN/PicImageSearch)

Anime search based on [trace.moe](https://soruly.github.io/trace.moe-api/#/) API

Integrated ChatGPT based on [ChatAnywhere](https://chatanywhere.apifox.cn/) v1 API

CloudFlare Workers proxy support based on [Cloudflare-Workers-Proxy](https://github.com/ymyuuu/Cloudflare-Workers-Proxy)

Self manga host using [Komga](https://github.com/gotson/komga)
