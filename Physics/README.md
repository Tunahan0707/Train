# Physics

Python ve PySide6 ile geliştirilen devre çizim ve DC çalışma noktası simülasyon uygulaması.

## Kurulum ve çalıştırma

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Testler

```powershell
python -m unittest discover -s tests -v
```

Testler Qt gerektiren dosyalarda `QT_QPA_PLATFORM=offscreen` kullanır. Bu test paketi henüz bu geliştirme oturumunda çalıştırılmadı; ilk yerel çalıştırmada çıkan hatalar ayrıca düzeltilmeli.

## Kullanım

- Alt çubuktaki kategori sekmelerinden bileşen çekmecesini aç; bileşeni sürükle veya tıklayarak ekle.
- Bileşenler otomatik R1, C1, V1 gibi referans adları alır. Ad ve değer sembolün altında görünür; sağdaki panelden düzenlenebilir.
- Shift + orta tuş kutu seçimi; orta tuş alanı kaydırma.
- R döndürür, Ctrl+D çoğaltır, Ctrl+Z / Ctrl+Y geri alır / yineler.
- Fare tekerleği yakınlaştırır; Ctrl+0 görünümü sıfırlar.
- Bağlantı kategorisinden İletken aracını seç. İlk tıklama başlangıç, ikinci tıklama bitiş noktasıdır. Uçlara ve mevcut kablo segmentlerine yakalama yapılır. Escape aracı iptal eder.
- Kablolar seçilip bütün olarak taşınabilir; tek tek uç/köşe düzenleme henüz yoktur.
- Üstteki **+** yeni devre sekmesi açar. Menüden devreyi yeniden adlandırabilir veya çoğaltabilirsin. Sekmeler taşınabilir ve kapatılabilir.
- Kaydetme tüm devre sekmelerini tek `.physics` proje dosyasına yazar. Eski tek devre dosyaları da içe aktarılır.
- Menüden Bağlantı Analizi ve DC Çözümü çalıştırılır. Çözümden sonra bir bileşeni seçerek sağ panelde hesaplanan değerleri inceleyebilirsin. Elektriksel düzenleme yapılınca eski ölçümler geçersiz kılınır.

## Mevcut DC model kapsamı

| Bileşen | DC yaklaşımı | Sınırlama |
|---|---|---|
| Direnç | Ohmik direnç; V/I/P | Tolerans, ısıl davranış ve güç sınırı yok |
| Kondansatör | Kararlı DC'de açık devre | Şarj/deşarj geçici rejimi yok |
| Bobin | Kararlı DC'de ideal kısa devre | Geçici rejim, sargı direnci ve doyum yok |
| Diyot / LED | Sabit ileri eşik + seri direnç, kesim/iletim durumu | Üretici eğrisi, ters kırılma ve sıcaklık yok |
| BJT / N-MOSFET | Eşik kontrollü basit anahtar yaklaşımı | Gerçek kazanç/transfer eğrileri ve parazitler yok |
| Sigorta | Girilen sabit direnç | Akım-zaman, ısınma ve atma davranışı yok |
| Potansiyometre | Üç uçlu direnç bölücü; sürgü oranı düzenlenebilir | Temas direnci ve tolerans yok |
| Anahtar | Açık devre / ideal sıfır voltlu kapalı dal | Temas direnci ve anahtarlama dinamiği yok |
| DC kaynak / pil | İdeal gerilim kaynağı | İç direnç, akım sınırlama ve pil kapasitesi yok |
| AC kaynak | Henüz desteklenmiyor | Dalga biçimi ve geçici rejim çözümü yok |

Desteklenmeyen bileşen varsa çözücü sessizce yok saymak yerine analizi durdurur. Diyot ve transistor yaklaşımları eğitim amaçlı basitleştirilmiş modellerdir; gerçek üretici modelleri değildir.

## Henüz tamamlanmayan büyük işler

- RLC geçici rejim ve AC dalga biçimi simülasyonu.
- Tam BJT/MOSFET modelleri; kaynak iç direnci ve pil davranışı.
- Uç/köşe tutamaçları, junction nesneleri ve daha kapsamlı topoloji düzenleme.
- Hiyerarşik özel devre bileşenleri: port tanımlama, başka devreye yerleştirme ve iç devreyi açıp düzenleme.
- Voltmetre/ampermetre/multimetre/oscilloscope gibi ayrı ölçü aletleri; şu anda DC çözücünün hesapladığı bileşen değerleri gösterilir.
- Isıl hasar, sigorta atması, aşırı akım/gerilim tanıları, simülasyon zaman çizelgesi ve otomatik kurtarma.

Ayrıntılı teknik durum, test kapsamı ve aşamalı geliştirme planı: `IMPLEMENTATION_AUDIT.md`.
