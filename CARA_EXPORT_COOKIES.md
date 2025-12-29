# 🍪 Cara Export Cookies dari Chrome untuk YouTube

## 📌 Kenapa Perlu Cookies?

YouTube mendeteksi bot dan memerlukan autentikasi. Dengan menggunakan cookies dari akun yang sudah login, bot bisa bypass deteksi ini.

---

## ✅ Method 1: Menggunakan Extension Chrome (RECOMMENDED)

### **1️⃣ Install Extension**

Buka Chrome dan install extension **"Get cookies.txt LOCALLY"**:

🔗 **Link Extension:**  
https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc

**Atau cari di Chrome Web Store:** `Get cookies.txt LOCALLY`

> ⚠️ **PENTING:** Gunakan yang "LOCALLY" bukan yang "Export" biasa. Extension ini lebih aman karena tidak upload cookies ke server.

---

### **2️⃣ Login ke YouTube**

1. Buka https://www.youtube.com di Chrome
2. Login dengan akun Google Anda
3. Pastikan sudah login penuh (bisa play video, dll)

---

### **3️⃣ Export Cookies**

1. **Tetap di halaman YouTube** (youtube.com)
2. **Klik icon extension** "Get cookies.txt LOCALLY" di toolbar Chrome (pojok kanan atas)
3. Akan muncul popup, klik **"Export"** atau **"Download"**
4. File `cookies.txt` akan terdownload otomatis

---

### **4️⃣ Pindahkan File ke Project**

1. File yang terdownload biasanya bernama `youtube.com_cookies.txt` atau `cookies.txt`
2. **Copy file tersebut** ke folder project bot (sama dengan lokasi `main.py`)
3. **Rename file menjadi:** `cookies.txt`

Struktur folder seharusnya seperti ini:
```
Project Debian Server CLI ONly/
├── main.py
├── cookies.txt          ← File cookies di sini
├── .env
├── bot/
└── ...
```

---

### **5️⃣ Set Path di .env**

Buka file `.env` dan pastikan ada:

```env
YOUTUBE_COOKIES_FILE=cookies.txt
COOKIES_FROM_BROWSER=
```

---

### **6️⃣ Restart Bot**

```bash
python main.py
```

Anda akan melihat log:
```
Using cookies from file: cookies.txt
```

---

## ✅ Method 2: Export Manual dari Browser (Alternative)

### **1️⃣ Buka Developer Tools di Chrome**

1. Login ke YouTube (youtube.com)
2. Tekan **F12** atau **Ctrl+Shift+I**
3. Buka tab **"Application"** (atau **"Storage"** di beberapa versi)

---

### **2️⃣ Lihat Cookies**

1. Di sidebar kiri, expand **"Cookies"**
2. Klik **"https://www.youtube.com"**
3. Anda akan melihat list semua cookies

---

### **3️⃣ Export ke Format Netscape**

**Buat file `cookies.txt`** dengan format berikut:

```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	CONSENT	YES+
.youtube.com	TRUE	/	TRUE	1735689600	VISITOR_INFO1_LIVE	xxxxxxxxxxxxx
.youtube.com	TRUE	/	FALSE	1735689600	PREF	f4=4000000
.youtube.com	TRUE	/	TRUE	1735689600	YSC	xxxxxxxxxxxx
```

**Format per baris:**
```
domain	flag	path	secure	expiration	name	value
```

> ⚠️ **Cara ini lebih ribet!** Lebih baik pakai Extension (Method 1)

---

## ✅ Method 3: Menggunakan EditThisCookie Extension

### **1️⃣ Install Extension**

🔗 https://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg

---

### **2️⃣ Export Cookies**

1. Login ke YouTube
2. Klik icon **EditThisCookie** di toolbar
3. Klik icon **"Export"** (ikon folder dengan panah)
4. Copy semua text yang muncul
5. Paste ke file `cookies.json`

---

### **3️⃣ Convert ke Netscape Format**

Gunakan online tool atau script Python untuk convert dari JSON ke Netscape format.

> ⚠️ **Cara ini juga ribet!** Tetap lebih mudah pakai "Get cookies.txt LOCALLY"

---

## 🔒 Keamanan Cookies

⚠️ **PENTING - Jaga Keamanan Cookies:**

- ❌ **JANGAN upload cookies.txt ke GitHub/public repo**
- ❌ **JANGAN share file cookies ke orang lain**
- ✅ Tambahkan `cookies.txt` ke `.gitignore`
- ✅ Simpan file cookies di local server saja
- 🔄 Update cookies jika sudah expired (biasanya 6 bulan - 1 tahun)

**File `.gitignore` sudah include:**
```
cookies.txt
*.txt
!requirements.txt
```

---

## 🔧 Troubleshooting

### **Error: "No such file 'cookies.txt'"**

✅ Pastikan file `cookies.txt` ada di root folder project  
✅ Atau gunakan path absolut di .env:
```env
YOUTUBE_COOKIES_FILE=C:/Users/ACER/Documents/project/cookies.txt
```

---

### **Error: "HTTP Error 403: Forbidden"**

✅ Cookies mungkin expired, export ulang dari browser  
✅ Pastikan format file benar (Netscape format)  
✅ Login ulang ke YouTube dan export cookies baru

---

### **Bot tetap error "Sign in to confirm"**

✅ Hapus cache browser dan login ulang  
✅ Export cookies dari Chrome (jangan dari Incognito)  
✅ Pastikan account YouTube tidak ter-restrict  
✅ Coba logout dan login ulang ke YouTube sebelum export

---

## 📚 Resources

- **Extension (Recommended):** [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
- **Alternative:** [EditThisCookie](https://chromewebstore.google.com/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
- **yt-dlp docs:** https://github.com/yt-dlp/yt-dlp#authentication-with-cookies

---

## ✅ Checklist

- [ ] Install extension "Get cookies.txt LOCALLY" di Chrome
- [ ] Login ke YouTube dengan akun Google
- [ ] Export cookies menggunakan extension
- [ ] Rename file menjadi `cookies.txt`
- [ ] Copy ke folder project (sama dengan main.py)
- [ ] Update `.env` dengan `YOUTUBE_COOKIES_FILE=cookies.txt`
- [ ] Restart bot
- [ ] Verify: lihat log "Using cookies from file: cookies.txt"

---

**🎵 Setelah setup, bot Anda tidak akan lagi kena error YouTube bot detection!**
