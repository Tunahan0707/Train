# Physics

Python ve PySide6 ile geliştirilen devre çizim ve simülasyon projesi.

## Çalıştırma

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Şu an kullanılabilenler

- Direnç, kondansatör, bobin, sigorta, potansiyometre, diyot, LED, BJT, MOSFET, DC/AC kaynak, pil, anahtar ve GND sembollerini yerleştirme.
- İletken çizme: Tel aracını seç, başlangıç noktasına ve bitiş noktasına tıkla. Tel uçları yakındaki bileşen uçlarına veya ızgaraya oturur.
- Sol tıkla seçme ve taşıma; orta tuşla dikdörtgen çoklu seçim.
- Shift + orta tuşla çalışma alanını kaydırma.
- Shift + sağ tıkla nesne silme; Delete ile seçili nesneleri silme.
- R ile seçili bileşenleri 90° döndürme.
- Ctrl + D ile seçili bileşenleri çoğaltma.
- Ctrl + Z / Ctrl + Y ile geri alma ve yineleme.
- Fare tekerleğiyle yakınlaştırma; Ctrl + 0 ile yakınlaştırmayı sıfırlama.
- F11 ile tam ekran.
- Özellikler panelinden seçili bileşenin gösterilen değerini değiştirme.
- Ctrl + N / Ctrl + O / Ctrl + S ile yeni devre, açma ve kaydetme.
- Devre → Bağlantıları denetle ile uç noktaları ve T-bağlantılarını içeren temel netlist analizi.

## Önemli sınır

Şu anki bileşenler şematik çizim nesneleridir. Tel uçları ve T-bağlantıları üzerinden temel elektriksel düğüm/netlist analizi yapılabilir. İki telin yalnızca çapraz kesişmesi bağlantı sayılmaz. Bu netlist henüz devre simülasyonunda kullanılmıyor. Gerçek bileşen modelleri, devre çözümleyicisi, akım/gerilim hesapları ve hasar fiziği henüz uygulanmadı.

Proje dosyaları `.physics` uzantısıyla JSON tabanlı olarak kaydedilir.
