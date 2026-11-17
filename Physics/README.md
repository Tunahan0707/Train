# Physics

Python ve PySide6 ile geliştirilen devre çizim ve simülasyon projesi.

## Çalıştırma

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Kullanım

- Bileşenleri sol panelden çalışma alanına sürükleyip bırak.
- İstenmeyen nesneleri çöp kutusuna sürükle.
- Orta tuşla kutu seçimi, Shift + orta tuşla alanı kaydırma.
- R ile döndürme, Ctrl + D ile çoğaltma.
- Ctrl + Z / Ctrl + Y ile geri alma ve yineleme.
- Fare tekerleğiyle yakınlaştırma; Ctrl + 0 ile sıfırlama.
- Üstteki anahtarla koyu/açık temayı değiştir.
- Özellikler panelinden seçili bileşenin değerini düzenle.
- Ctrl + N / Ctrl + O / Ctrl + S ile yeni devre, açma ve kaydetme.
- Devre menüsünden bağlantı analizi, Simülasyon menüsünden DC çözümü.

## Önemli sınır

Şu anki bileşenler şematik çizim nesneleridir. Tel uçları ve T-bağlantıları üzerinden temel elektriksel düğüm/netlist analizi yapılabilir. İki telin yalnızca çapraz kesişmesi bağlantı sayılmaz. Bu netlist henüz devre simülasyonunda kullanılmıyor. DC çözümleyici yalnızca direnç ve ideal DC kaynaklarını çözer. Diyot, LED, transistör, kondansatör, bobin, anahtar ve AC kaynak modelleri henüz çözülmez. Gerçek bileşen modelleri ve hasar fiziği henüz uygulanmadı.

Proje dosyaları `.physics` uzantısıyla JSON tabanlı olarak kaydedilir.
