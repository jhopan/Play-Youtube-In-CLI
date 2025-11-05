# 🔊 Manual MPV Volume Control Commands

## 📝 Perintah Manual untuk Test Volume

Bot sekarang support **2 metode** kontrol volume:

1. **MPV IPC** (jika tersedia) - untuk kontrol volume di MPV saja
2. **System Volume** via `amixer` - untuk kontrol volume system (RECOMMENDED)

## 🎯 Method 1: System Volume Control (RECOMMENDED)

### **Install amixer (jika belum):**

```bash
sudo apt install alsa-utils -y
```

### **Naikkan Volume 5%:**

```bash
amixer -D pulse sset Master 5%+
```

### **Turunkan Volume 5%:**

```bash
amixer -D pulse sset Master 5%-
```

### **Set Volume ke Level Tertentu:**

```bash
# Set ke 25%
amixer -D pulse sset Master 25%

# Set ke 50%
amixer -D pulse sset Master 50%

# Set ke 75%
amixer -D pulse sset Master 75%

# Set ke 100% (maksimal)
amixer -D pulse sset Master 100%
```

### **Toggle Mute:**

```bash
amixer -D pulse sset Master toggle
```

### **Unmute:**

```bash
amixer -D pulse sset Master unmute
```

### **Check Current Volume:**

```bash
amixer -D pulse get Master
```

## 🎯 Method 2: MPV IPC Socket (Advanced)

#### Check Socket Exists:

```bash
ls -l /tmp/mpvsocket
```

#### Test Naikkan Volume (Manual):

```bash
# Set volume ke 75%
echo '{ "command": ["set_property", "volume", 75] }' | socat - /tmp/mpvsocket

# Set volume ke 100% (maksimal)
echo '{ "command": ["set_property", "volume", 100] }' | socat - /tmp/mpvsocket

# Set volume ke 50%
echo '{ "command": ["set_property", "volume", 50] }' | socat - /tmp/mpvsocket
```

#### Get Current Volume:

```bash
echo '{ "command": ["get_property", "volume"] }' | socat - /tmp/mpvsocket
```

### 2. **Install socat (Jika Belum Ada)**

```bash
sudo apt install socat -y
```

### 3. **Alternative: Python Script untuk Test**

Save as `test_volume.py`:

```python
#!/usr/bin/env python3
import socket
import json
import sys

def send_mpv_command(command):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect('/tmp/mpvsocket')

        command_str = json.dumps(command) + '\n'
        sock.send(command_str.encode('utf-8'))

        response = sock.recv(4096).decode('utf-8')
        sock.close()

        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./test_volume.py <volume>")
        print("Example: ./test_volume.py 75")
        sys.exit(1)

    volume = int(sys.argv[1])
    command = {"command": ["set_property", "volume", volume]}
    send_mpv_command(command)
```

Jalankan:

```bash
chmod +x test_volume.py
./test_volume.py 100  # Set to 100%
./test_volume.py 50   # Set to 50%
```

### 4. **Perintah MPV Lainnya**

#### Pause/Resume:

```bash
# Pause
echo '{ "command": ["set_property", "pause", true] }' | socat - /tmp/mpvsocket

# Resume
echo '{ "command": ["set_property", "pause", false] }' | socat - /tmp/mpvsocket
```

#### Get Playback Position:

```bash
echo '{ "command": ["get_property", "time-pos"] }' | socat - /tmp/mpvsocket
```

#### Get Duration:

```bash
echo '{ "command": ["get_property", "duration"] }' | socat - /tmp/mpvsocket
```

#### Seek (Skip Forward/Backward):

```bash
# Skip 10 seconds forward
echo '{ "command": ["seek", 10] }' | socat - /tmp/mpvsocket

# Skip 10 seconds backward
echo '{ "command": ["seek", -10] }' | socat - /tmp/mpvsocket
```

### 5. **Check MPV Process & Volume**

```bash
# Check if MPV is running
ps aux | grep mpv

# Check MPV command line (lihat volume yang diset)
ps aux | grep mpv | grep volume

# Check socket
lsof | grep mpvsocket
```

### 6. **Test dengan Bot**

Di Telegram bot:

1. Load video/playlist
2. Klik button **Volume**
3. Pilih 25%, 50%, 75%, atau 100%
4. Volume akan berubah **secara live** tanpa restart

## 🧪 Quick Test Script

Save as `quick_test_volume.sh`:

```bash
#!/bin/bash

echo "🔊 MPV Volume Control Test"
echo "=========================="
echo ""

# Check if socket exists
if [ ! -S "/tmp/mpvsocket" ]; then
    echo "❌ MPV socket not found!"
    echo "   Make sure bot is running and playing a song"
    exit 1
fi

echo "✅ MPV socket found"
echo ""

# Test commands
echo "🔊 Setting volume to 100%..."
echo '{ "command": ["set_property", "volume", 100] }' | socat - /tmp/mpvsocket
sleep 2

echo "🔉 Setting volume to 50%..."
echo '{ "command": ["set_property", "volume", 50] }' | socat - /tmp/mpvsocket
sleep 2

echo "🔊 Setting volume to 75%..."
echo '{ "command": ["set_property", "volume", 75] }' | socat - /tmp/mpvsocket

echo ""
echo "✅ Test complete!"
echo ""
echo "Did you hear the volume change?"
```

Run:

```bash
chmod +x quick_test_volume.sh
./quick_test_volume.sh
```

## 📊 Troubleshooting

### Socket Not Found

```bash
# Check if MPV is running with IPC
ps aux | grep "input-ipc-server"

# If not found, bot needs update
cd ~/Play-Youtube-In-CLI
git pull
python main.py
```

### socat Not Found

```bash
sudo apt install socat -y
```

### Permission Denied

```bash
# Check socket permissions
ls -l /tmp/mpvsocket

# Should be readable/writable by your user
# If not, run bot as same user
```

### No Audio Change

1. Check if audio device working:

```bash
speaker-test -t wav -c 2 -l 1
```

2. Check PulseAudio:

```bash
pulseaudio --check && echo "Running" || echo "Not running"
```

3. Restart bot:

```bash
python main.py
```

## 💡 Tips

- **Volume di bot** (25/50/75/100) adalah relatif ke system volume
- **System volume** harus sudah cukup tinggi (pakai `alsamixer` atau `pactl`)
- **Bot volume control** sekarang **real-time** (tidak perlu restart lagu)

## 🎵 System Volume Commands

### Check System Volume:

```bash
# ALSA
alsamixer

# PulseAudio
pactl list sinks | grep -A 10 "Sink #"
```

### Set System Volume:

```bash
# ALSA (Master channel)
amixer set Master 80%

# PulseAudio
pactl set-sink-volume @DEFAULT_SINK@ 80%
```

### Unmute:

```bash
# ALSA
amixer set Master unmute

# PulseAudio
pactl set-sink-mute @DEFAULT_SINK@ 0
```

---

## ✅ Test Checklist

- [ ] Install socat: `sudo apt install socat -y`
- [ ] Bot running dengan lagu playing
- [ ] Socket exists: `ls -l /tmp/mpvsocket`
- [ ] Test manual: `echo '{ "command": ["set_property", "volume", 100] }' | socat - /tmp/mpvsocket`
- [ ] Test via Telegram bot: Click Volume button
- [ ] Audio berubah secara real-time

**Sekarang bot support real-time volume control!** 🎉🔊
