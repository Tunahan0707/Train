# Physics

Python ve PySide6 ile geliştirilen devre çizim ve simülasyon projesi.

## Çalıştırma

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Testler

Temel sayısal yardımcıları standart kütüphane ile test et:

```powershell
python -m unittest discover -s tests -v
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

## Mevcut teknik kapsam

Editörde direnç, kondansatör, bobin, diyot, LED, BJT, MOSFET, sigorta, potansiyometre, DC/AC kaynak, pil, anahtar, GND ve kablo sembolleri bulunur. Ancak sembolün bulunması, fiziksel modelinin tamamlandığı anlamına gelmez.

Netlist; bileşen uçlarını, kablo uçlarını, kablo segmentlerine temasları ve ortak GND referansını kullanarak temel bağlantı gruplarını çıkarır. Yalnızca kesişen iki kablo, uç/T bağlantısı yoksa bağlı sayılmaz. Kablolar seçilip bütün olarak taşınabilir; uç ve köşe düzenleme ile doğrudan uçtan uca kablo çizimi henüz yoktur.

DC çalışma noktası çözümü direnç, ideal DC gerilim kaynağı, pil, ideal kapalı anahtar, ideal kondansatör (açık devre) ve ideal bobin (kısa devre) modellerini kapsar. Desteklenmeyen bileşen varsa artık kısmi/yanıltıcı sonuç vermek yerine çözümü durdurur. Kondansatör/bobin geçici rejimi, yarı iletkenlerin doğrusal olmayan modelleri, AC analizi, ölçü aletleri, ısıl davranış ve hasar fiziği henüz tamamlanmamıştır.

Bir proje şu anda tek devre sahnesi içerir; bu devre adlandırılıp yeniden adlandırılabilir. Çoklu devre sekmeleri ve hiyerarşik özel devre bileşenleri henüz uygulanmamıştır. Gerçek kapsam ve sıralama için `IMPLEMENTATION_AUDIT.md` dosyasına bak.

Proje dosyaları `.physics` uzantısıyla JSON tabanlı olarak kaydedilir.


### Current incremental capabilities

- Component names are editable in the properties panel and saved in project format v2; version 1 projects remain readable.
- DC steady-state analysis includes ideal capacitors (open circuit) and ideal inductors (short circuit). This does not provide charging/discharging curves or transient waveforms.
- Unsupported component models are still rejected rather than silently omitted.

- Kablolar bütün olarak taşınabilir ve konumları kaydedilir.
- Bileşen adları özellikler panelinden, devre adı Menü üzerinden düzenlenebilir.
- Proje biçimi v2'dir; v1 dosyaları da açılabilir.
- Yeni eklenen bileşenler otomatik R1/C1/V1 gibi referans adları alır; ad ve değer sembolün altında gösterilir.
- Proje biçimi v3; bileşenlerin kararlı kimlikleri ve devre adı kaydedilir. v1/v2 dosyaları geriye dönük açılır.
