# Aero Gateway: Cloudflare Tunnel Setup Guide

To expose your local Aero Gateway (`localhost:8000`) through `https://api.ourspaceship.site`, follow these steps:

## 1. Install Cloudflared
If you haven't already, download and install the Cloudflare Tunnel client:
[Download Cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/)

## 2. Authentication
Login to your Cloudflare account from the terminal:
```bash
cloudflared tunnel login
```
Select your domain `ourspaceship.site` in the browser window that opens.

## 3. Create the Tunnel
Create a new tunnel named `aero-gateway`:
```bash
cloudflared tunnel create aero-gateway
```
*Note the Tunnel ID (UUID) provided in the output.*

## 4. Map to your Domain
Route your subdomain to the tunnel:
```bash
cloudflared tunnel route dns aero-gateway api.ourspaceship.site
```

## 5. Configuration File
Create a `config.yaml` file (usually in `.cloudflared` folder) with the following content:
```yaml
tunnel: <YOUR-TUNNEL-ID>
credentials-file: C:\Users\kaung myat thu\.cloudflared\<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: api.ourspaceship.site
    service: http://localhost:8000
    originRequest:
      httpHostHeader: api.ourspaceship.site
  - service: http_status:404
```

## 6. Run the Tunnel
Start the tunnel:
```bash
cloudflared tunnel run aero-gateway
```

## 7. Finalize Telegram Webhook
Once the tunnel is live, tell Telegram to send messages to your new URL. Paste this into your browser (replace `<BOT_TOKEN>`):

`https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://api.ourspaceship.site/api/v1/recorder/telegram/webhook&secret_token=aero_secure_secret_123`

---
**Security Note:** The `aero_secure_secret_123` is used by Aero to ensure only authorized messages from your tunnel are processed.
