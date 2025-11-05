# Notification Setup Guide

Get instant alerts when new TikTok reposts are detected! This guide will help you set up email and/or Telegram notifications.

## Quick Start

Edit your `.env` file and add notification settings. You can use **Email**, **Telegram**, or **both**!

## Option 1: Email Notifications (Recommended for SMS)

Email notifications work great and can forward to your phone via SMS gateways.

### Setup Steps:

1. **Using Gmail (Recommended):**

   a. Go to your Google Account: https://myaccount.google.com/apppasswords

   b. Create an "App Password" (you may need to enable 2-Step Verification first)

   c. Copy the 16-character password

2. **Update your `.env` file:**
   ```bash
   ENABLE_NOTIFICATIONS=true
   EMAIL_NOTIFICATIONS=true
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   NOTIFICATION_EMAIL=destination@example.com
   ```

3. **For SMS notifications via email:**
   Use your carrier's email-to-SMS gateway as the `NOTIFICATION_EMAIL`:

   - **AT&T**: `your_number@txt.att.net`
   - **T-Mobile**: `your_number@tmomail.net`
   - **Verizon**: `your_number@vtext.com`
   - **Sprint**: `your_number@messaging.sprintpcs.com`

   Example for AT&T:
   ```bash
   NOTIFICATION_EMAIL=5551234567@txt.att.net
   ```

### Other Email Providers:

**Outlook/Hotmail:**
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```bash
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

## Option 2: Telegram Notifications

Telegram is free, fast, and works worldwide!

### Setup Steps:

1. **Create a Telegram Bot:**

   a. Open Telegram and search for `@BotFather`

   b. Send `/newbot` and follow the instructions

   c. Copy your bot token (looks like: `123456789:ABCdefGhIJKlmNoPQRstuVWxyZ`)

2. **Get Your Chat ID:**

   a. Search for `@userinfobot` on Telegram

   b. Send any message to it

   c. It will reply with your chat ID (a number like: `123456789`)

3. **Start a chat with your bot:**

   a. Search for your bot by username (from step 1)

   b. Send `/start` to your bot

4. **Update your `.env` file:**
   ```bash
   ENABLE_NOTIFICATIONS=true
   TELEGRAM_NOTIFICATIONS=true
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWxyZ
   TELEGRAM_CHAT_ID=123456789
   ```

## Using Both Email and Telegram

You can enable both! Just set both to `true` in your `.env`:

```bash
ENABLE_NOTIFICATIONS=true
EMAIL_NOTIFICATIONS=true
TELEGRAM_NOTIFICATIONS=true
# ... add all the credentials for both
```

## Testing Your Setup

After configuring notifications, test them locally:

1. Create a test script `test_notifications.py`:
   ```python
   from notifications import NotificationService
   from config import Config

   Config.validate()
   notifier = NotificationService()
   notifier.test_notifications()
   ```

2. Run it:
   ```bash
   python test_notifications.py
   ```

You should receive a test notification!

## Deploying to AWS

After setting up notifications locally, deploy to AWS:

```bash
./deploy.sh ~/.ssh/tiktoklog.pem 3.145.68.9
```

The script will copy your `.env` file with notification settings to the server.

## Troubleshooting

### Email Issues:

**"Authentication failed"**
- Make sure you're using an App Password, not your regular password
- Verify 2-Step Verification is enabled on your Google account

**"Connection refused"**
- Check your SMTP host and port settings
- Some networks block port 587 - try port 465 with SSL

**Not receiving emails**
- Check your spam folder
- Verify the destination email address is correct

### Telegram Issues:

**"Bot not responding"**
- Make sure you sent `/start` to your bot first
- Verify the bot token is correct

**"Chat not found"**
- Verify your chat ID is correct
- Make sure you've started a conversation with the bot

**Not receiving messages**
- Check that your bot token and chat ID are both correct
- Ensure there are no typos in your `.env` file

## Security Notes

- Never commit your `.env` file to git (it's in `.gitignore`)
- Use App Passwords, not your main email password
- Keep your bot token secret
- The notification settings are only stored locally and on your EC2 instance

## What You'll Receive

When new reposts are detected, you'll get:

- **Email**: HTML email with clickable links to all new reposts
- **Telegram**: Formatted message with links to all new reposts
- Both include the count and timestamp

Example notification:
```
🎵 3 New TikTok Reposts Detected!

Found 3 new reposts from @user:

1. https://www.tiktok.com/@user1/video/123...
2. https://www.tiktok.com/@user2/photo/456...
3. https://www.tiktok.com/@user3/video/789...
```
