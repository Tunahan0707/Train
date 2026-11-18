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

Netlist; bileşen uçlarını, kablo uçlarını, kablo segmentlerine temasları ve ortak GND referansını kullanarak temel bağlantı gruplarını çıkarır. Yalnızca kesişen iki kablo, uç/T bağlantısı yoksa bağlı sayılmaz. Bağlantı kategorisinden İletken aracını seç; ilk tıklamayla başlangıcı, ikinci tıklamayla bitişi belirle. Araç bileşen uçlarına ve mevcut kablo segmentlerine yakındaki noktaları yakalar. Kablolar ayrıca seçilip bütün olarak taşınabilir; uç/köşe tutamaçları henüz yoktur.

DC çalışma noktası çözümü direnç, ideal DC gerilim kaynağı, pil, ideal kapalı anahtar, ideal kondansatör (açık devre) ve ideal bobin (kısa devre) modellerini kapsar. Desteklenmeyen bileşen varsa artık kısmi/yanıltıcı sonuç vermek yerine çözümü durdurur. Kondansatör/bobin geçici rejimi, BJT/MOSFET modelleri ve yarı iletkenlerin ayrıntılı doğrusal olmayan fiziği, AC analizi, ölçü aletleri, ısıl davranış ve hasar fiziği henüz tamamlanmamıştır.

Bir proje birden fazla devre sekmesi içerebilir. Sekmeler eklenebilir, yeniden adlandırılabilir, sıralanabilir ve kapatılabilir. Eski tek devre dosyaları tek sekmeli projeye aktarılır. Hiyerarşik, yeniden kullanılabilir özel devre bileşenleri henüz uygulanmamıştır. Gerçek kapsam ve sıralama için `IMPLEMENTATION_AUDIT.md` dosyasına bak.

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

- Üstteki sekme çubuğundaki **+** ile yeni devre oluştur; sekme adına Menü → Devreyi yeniden adlandır ile ad ver.
- Kaydetme işlemi açık projedeki bütün devre sekmelerini birlikte kaydeder.

- İletken çiziminden Escape ile çıkılır; kablo oluşturma Ctrl+Z ile geri alınabilir.

- Diyot/LED DC çözümü basitleştirilmiş parçalı doğrusal modeldir (eşik gerilimi + seri direnç); gerçek üretici modeli veya sıcaklık etkisi değildir.

- DC çözümünden sonra bir bileşeni seçerek sağdaki özellikler panelinde o bileşenin hesaplanan gerilim, akım ve güç değerlerini görebilirsin. Devre değiştiğinde eski ölçüm otomatik geçersiz kılınır.

- Sigorta DC modelinde girilen sabit dirençle hesaplanır; atma/ısınma davranışı henüz yoktur.
- Potansiyometrenin toplam direncini ve özellikler panelindeki sürgü oranını (0–1) düzenleyebilirsin; DC çözümü üç uçlu gerilim bölücüyü hesaplar.

- BJT ve N-kanal MOSFET şu an yalnızca eşik gerilimine bağlı basit anahtar yaklaşımıyla çözülür. Bu, gerçek transistor kazanç/eğri modeli değildir; BJT baz akımı ve MOSFET gövde diyodu hesaba katılmaz.

- Menü → Devreyi çoğalt ile etkin devrenin tüm bileşenlerini, kablolarını, değerlerini ve anahtar durumlarını yeni bir sekmeye kopyala.
