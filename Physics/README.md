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

- Alt çubuktaki kategori sekmesine basarak bileşen çekmecesini yukarı aç.
- Bileşenleri çalışma alanına sürükle veya tek tıklamayla ekranın ortasına ekle.
- Shift basılıyken bileşen düğmesine tıklayarak aynı hizada alt alta yeni bileşenler ekle; eklenenler birlikte seçili kalır.
- Normal ekleme ve sürükle-bırak sonrasında kategori çekmecesi kapanır.
- Orta tuşla kutu seçimi, Shift + orta tuşla alanı kaydırma.
- R ile döndürme, Ctrl + D ile çoğaltma.
- Ctrl + Z / Ctrl + Y ile geri alma ve yineleme.
- Fare tekerleğiyle yakınlaştırma; Ctrl + 0 ile sıfırlama.
- Üstteki güneş/ay göstergeli anahtarla koyu/açık temayı değiştir.
- Sağdaki özellikler paneli seçili bileşenlerin ortak özelliklerini düzenler; farklı türler ayrı bölümlerde gösterilir.
- Alt çubuktaki Menü üzerinden devre oluşturma, açma, kaydetme, bağlantı analizi ve DC çözümüne ulaş.

## Önemli sınır

Şu anki bileşenler şematik çizim nesneleridir. Tel uçları ve T-bağlantıları üzerinden temel elektriksel düğüm/netlist analizi yapılabilir. İki telin yalnızca çapraz kesişmesi bağlantı sayılmaz. Bu netlist henüz devre simülasyonunda kullanılmıyor. DC çözümleyici yalnızca direnç ve ideal DC kaynaklarını çözer. Diyot, LED, transistör, kondansatör, bobin, anahtar ve AC kaynak modelleri henüz çözülmez. Gerçek bileşen modelleri ve hasar fiziği henüz uygulanmadı.

Proje dosyaları `.physics` uzantısıyla JSON tabanlı olarak kaydedilir.
