# 🔇 Fix: No Audio on Headless Server

## 🐛 Problem

Bot jalan, tapi tidak ada suara di server karena:

- Server headless (CLI only, no GUI)
- Tidak ada audio output device
- MPV tidak tahu kemana output audio

## ✅ Solution: Install Dummy Audio Driver

### Option 1: PulseAudio Dummy (Recommended)

```bash
# Install PulseAudio
sudo apt update
sudo apt install pulseaudio pulseaudio-utils -y

# Start PulseAudio in system mode
pulseaudio --start --log-target=syslog

# Or create dummy sink
pactl load-module module-null-sink sink_name=dummy

# Test
pactl info
```

### Option 2: ALSA Dummy Driver

```bash
# Load ALSA dummy module
sudo modprobe snd-dummy

# Make it permanent
echo "snd-dummy" | sudo tee -a /etc/modules

# Verify
aplay -l
```

### Option 3: Use ALSA Config

Create ALSA config file:

```bash
# Create config
sudo tee /etc/asound.conf > /dev/null << 'EOF'
pcm.!default {
    type plug
    slave.pcm "null"
}

pcm.null {
    type null
}
EOF

# Test
speaker-test -t wav -c 2
```

## 🎵 Bot Configuration for Headless

Bot sudah configured untuk headless (`--no-video`), tapi perlu audio output.

### Update MPV Options

Edit `.env` atau bot config untuk tambah audio output:

```bash
# In your server, test MPV
mpv --audio-device=help

# Find available audio device, contoh:
# - pulse (PulseAudio)
# - alsa (ALSA)
# - null (No output, for testing)
```

## 🔧 Quick Fix (Recommended)

```bash
cd ~/Play-Youtube-In-CLI

# Install PulseAudio
sudo apt install pulseaudio -y

# Start PulseAudio
pulseaudio --start

# Verify it's running
pulseaudio --check && echo "✓ PulseAudio is running"

# Test MPV with PulseAudio
mpv --audio-device=pulse "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-video

# If working, restart bot
python main.py
```

## 🎧 For Physical Audio Output

Jika server punya audio output (speaker/headphone):

### Check Audio Devices

```bash
# List audio devices
aplay -l

# List PulseAudio sinks
pactl list short sinks

# Set default sink
pactl set-default-sink <sink_name>
```

### Test Audio

```bash
# Test with speaker-test
speaker-test -t wav -c 2 -l 1

# Test with MPV
mpv --no-video "https://www.youtube.com/watch?v=test"
```

## 🚀 Auto-Setup Script

Save as `setup_audio.sh`:

```bash
#!/bin/bash

echo "🔊 Setting up audio for headless server..."

# Install PulseAudio
echo "📦 Installing PulseAudio..."
sudo apt update
sudo apt install pulseaudio pulseaudio-utils -y

# Configure PulseAudio for system-wide use
echo "⚙️  Configuring PulseAudio..."
sudo tee /etc/systemd/user/pulseaudio.service > /dev/null << 'EOF'
[Unit]
Description=PulseAudio Sound System
Requires=pulseaudio.socket

[Service]
Type=notify
ExecStart=/usr/bin/pulseaudio --daemonize=no --system --disallow-exit --disallow-module-loading
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# Start PulseAudio
echo "▶️  Starting PulseAudio..."
pulseaudio --start --log-target=syslog || pulseaudio -D

# Create dummy sink for testing
echo "🔇 Creating dummy audio sink..."
pactl load-module module-null-sink sink_name=dummy

# Verify
echo ""
echo "✅ Audio setup complete!"
echo ""
echo "Test with:"
echo "  mpv --no-video --audio-device=pulse 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
echo ""
echo "Available audio devices:"
pactl list short sinks
```

Run it:

```bash
chmod +x setup_audio.sh
./setup_audio.sh
```

## 🔍 Troubleshooting

### MPV Can't Find Audio Device

```bash
# Check MPV audio devices
mpv --audio-device=help

# Try different audio drivers
mpv --ao=pulse ...  # PulseAudio
mpv --ao=alsa ...   # ALSA
mpv --ao=null ...   # No output (silent)
```

### PulseAudio Not Running

```bash
# Check status
pulseaudio --check
echo $?  # 0 = running, 1 = not running

# Start manually
pulseaudio --start

# Or kill and restart
pulseaudio --kill
pulseaudio --start
```

### Permission Issues

```bash
# Add user to audio group
sudo usermod -a -G audio $USER

# Logout and login again
exit
```

## 🎛️ Advanced: Remote Audio Streaming

Jika mau dengar audio dari computer lain:

### 1. PulseAudio Network Streaming

**On Server:**

```bash
# Enable network streaming
pactl load-module module-native-protocol-tcp auth-anonymous=1
```

**On Client (Your Computer):**

```bash
# Connect to server
export PULSE_SERVER=tcp:your-server-ip:4713
pavucontrol  # Control remote audio
```

### 2. SSH Audio Forwarding

```bash
# SSH with X11 forwarding
ssh -X user@server

# PulseAudio will forward automatically
```

## 💡 For Testing Only (Silent Mode)

Jika cuma mau test bot tanpa audio:

```bash
# Edit MPV command to use null audio
mpv --ao=null --no-video "url"
```

Update `bot/core/mpv_player.py`:

```python
cmd.append('--ao=null')  # Silent mode for testing
```

## 📝 Summary

**Quick solution untuk production:**

```bash
# 1. Install PulseAudio
sudo apt install pulseaudio -y

# 2. Start PulseAudio
pulseaudio --start

# 3. Test
mpv --audio-device=pulse --no-video "https://youtube.com/watch?v=test"

# 4. Run bot
cd ~/Play-Youtube-In-CLI
python main.py
```

**Bot akan jalan dan audio akan keluar** (jika server punya speaker), atau **akan jalan silent** (jika pure headless).

---

**Important:** Bot sudah jalan dengan baik! Audio output adalah optional untuk monitoring. Bot tetap berfungsi tanpa audio output.
