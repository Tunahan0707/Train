# BrainNew — Prototip durumu ve uygulama notları

Dal: `fix/brainnew-architecture-audit`
Temel tasarım sözleşmesi: `LOCAL_SYNAPTIC_DYNAMICS_DESIGN.md`

Bu belge tasarım sözleşmesinin yerine geçmez. Kesin kararlar korunur; kalibrasyon gerektiren sayısal değerler biyolojik sabit olarak sunulmaz; henüz kararlaştırılmamış davranışlar nihai tasarım kararı sayılmaz.

## Prototip çekirdeği

- `Beyin.py`: Simülasyon saati, deterministik olay kuyruğu, ayrı nöron/bağlantı uzamsal indeksleri ve bileşenler arası koordinasyon. Membranı güncellemez, eşik kontrolü yapmaz, çıkış sinapsı seçmez ve normal ağ akışında sinapsı aktive etmez; yalnızca nöronun aktive ettiği sinapsların iletimini zamanlar.
- `Noron.py`: Dendrit girdilerini bütünleştirir, membranı günceller, ateşlenme eşiğini değerlendirir, aksiyon potansiyelini başlatır, uygun çıkış sinapslarını seçip aktive eder, terminal kimyasal salımını başlatır, kendi faz döngüsünü yönetir ve yerel kimyasal/reseptör uygunluğuna göre yeni bağlantı hedefini seçer.
- `Dendrid.py`: İşaretli girdileri tamponlar, transmitter reseptör yanıtını yerel sinyale modülatör olarak ekler, dendrit-sinaps katkılarını taşır ve büyüme sinyaline reseptör uygunluğunu hesaplar.
- `Baglanti.py`: Yerel aktivasyon potansiyeli, eşik, lazy sönüm, etkinlik izi, hedefe iletim gecikmesi, terminal transmitter repertuvarı ve mikroglianın değerlendirdiği yapısal durum/bakım parametrelerini taşır.
- `KimyasalAlan.py`: Transmitter türlerini ayrı tutan 2B analitik difüzyon/sönüm alanı.

## Olay akışı ve sorumluluk sınırı

1. Beyin duyusal veya sinaptik girdiyi hedef nörona iletir.
2. Nöron girdiyi kendi dendrit tamponuna alır.
3. Beyin yalnızca bir entegrasyon zamanı planlar; aynı nöron ve aynı zaman için yinelenen entegrasyon olaylarını tekilleştirir.
4. Entegrasyon anında nöron kendi girdilerini birleştirir, dendritik sinaps katkılarını günceller, membranını değerlendirir ve gerekiyorsa ateşlenir.
5. Nöron yalnızca yerel potansiyeli eşiği karşılayan çıkış sinapslarını seçer ve aktive eder; terminalin kimyasal salımını da sinapsın yerel mekanizması yürütür.
6. Beyin aktive edilmiş sinapsların hedefe iletim olaylarını zamanlar.
7. Faz geçişlerini nöronun kendi faz mekanizması yürütür; Beyin yalnızca sonraki faz olayının zamanını kuyruğa koyar.

Aynı zaman damgasındaki olaylarda girdi olayları entegrasyondan önce, faz geçişleri entegrasyondan önce işlenir. Eşit öncelik ve zamanda kararlı olay kimliği sırası korunur. Olay gecikmesi pozitif ve sonlu olmalı; planlanan olay zamanı da sonlu kalmalıdır.

## Refrakter dönemde gelen girdiler — geçici uygulama

Tasarım sözleşmesi, refrakter girdinin bekletilmesi, sönümlenmesi veya kaybolması seçenekleri arasında nihai karar vermemiştir.

Bu düzeltme dalındaki geçici davranış:
- Refrakter sırada gelen girdi dendrit tamponunda korunur.
- Refrakter sırada gerçekleşen entegrasyon denemesi yeni ateşlenme başlatmaz ve tamponu temizlemez.
- Nöron dinlenmeye döndüğünde bekleyen girdiler için entegrasyon yeniden planlanır.

Bu, kaybolan/takılı kalan girdi hatasını önleyen geçici bir uygulama politikasıdır; tasarım sözleşmesindeki açık kararı kalıcı olarak kapatmaz. Alternatif sönüm veya atma davranışı eklenmemiştir.

## Mevcut çekirdek davranışları

- Nöron ateşlenmesi ve çıkış sinapsı aktivasyonu ayrı koşullardır.
- Nöron ateşlendiğinde yalnızca yerel eşiği geçen çıkış sinapsları aktive edilir.
- Aynı ateşlenme olayında uygun sinapslar seri rastgele seçimle değil, tek yerel seçim turuyla belirlenir.
- Bir sinapsa birden fazla dendritten gelen etkiler önce toplamsal hesaplanır; ardından o sinapsa gerçekten katkı veren dendrit sayısının kareköküyle normalize edilir.
- Dendrit-sinaps öğrenmesi yalnızca gerçekten katkı yükleyen çiftlerde yürür. İlk değerlendirme fırsatında negatif ceza uygulanmaz. Her katkı parametresi kendi alt/üst sınırları içinde tutulur; güncelleme yönündeki sınıra yaklaştıkça toplamsal adım küçülür. İlk prototip varsayılanı [-1, 1] olup biyolojik sabit değil, kalibrasyon parametresidir.
- Öğrenme uygunluğu yalnızca mevcut entegrasyon olayında katkı veren çiftlerden oluşur; ateşlenmeyen eski entegrasyonlardan kalan çiftler sonraki ateşlenmede yanlışlıkla cezalandırılmaz.
- Bir terminal aynı aktivasyonda repertuvarındaki birden fazla transmitter türünü salabilir. Her türün miktarı, terminale ait işaretli duyarlılık ve o ateşlenmede gerçekten katkı veren dendritik sinyalle toplamsal biçimde modüle edilebilir; repertuvar dışı tür üretilemez.
- Bağlantı yapısal bütünlüğünü ve bakım parametrelerini taşır; bağımsız `Mikroglia` ajanları kendi 2B konumları ve algılama yarıçapları içindeki bağlantıları uzamsal indeks üzerinden tarar. Mikroglia, kullanım izi, büyüme/stabilizasyon/budama kimyası ve yapısal bütünlüğü birlikte değerlendirir. Kullanılmama tek başına fiziksel kopma oluşturmaz; budama işareti ve düşük kullanım birlikte gerekir. Kopma kararını mikroglia verir; Beyin yalnızca bakım olayını zamanlar ve kopmuş bağlantıyı ağ kayıtlarından temizler. Bakım açıkça başlatılır; tekrarlanan bakım yalnızca `Beyin.calistir(son_zaman=...)` ile verilen sonlu simülasyon aralığında yürür. Sınırsız çalıştırmada sonsuz bakım olayı zincirine izin verilmez. İlk parametreler kalibrasyon amaçlıdır.
- Kimyasal alan kaynakları şimdilik saklanır ve sorguda taranır; büyük ağ ölçeği için optimize edilmiş değildir.
- Girdi, konum, olay zamanı, sinaps ve kimyasal kaynak parametrelerinde sonlu değer kontrolleri bulunur. Sinaps eşiği, potansiyelin [-1, 1] aralığıyla tutarlı tutulur; nöron yalnızca kendi kaynak olduğu çıkış sinapslarını kaydedebilir.

## Henüz uygulanmayan tasarım parçaları

Bunlar unutulmuş veya iptal edilmiş değildir; sonraki aşamalara bırakılmıştır.

- Yönlü sinaps-sinaps ilişkileri ve birlikte etkinleşme/etkinleşmeme öğrenmesi.
- Geriye doğru dallanan feedback ve dal başına iz eşiği.
- Farklı nöronların uzamsal/zamansal yakınlıkla birlikte ateşlenme etkileşimi.
- Bağımsız mikroglia ajanları ve açıkça planlanan bakım olayları ilk uygulama düzeyinde vardır; otomatik periyodik zamanlama, sinyal ailelerinin biyolojik ayrıntısı ve parametre kalibrasyonu henüz tamamlanmamıştır.
- Mevcut bağlantının kademeli onarımı ve bağlantısız nöronun toparlanma modu. Kontrollü yeni bağlantı oluşumu ilk sürümde vardır; otomatik büyüme zamanlaması, olgunlaşma dinamiği ve görev düzeyinde değerlendirme henüz yoktur.
- Reseptör organı ve motor organı üzerinden tam duyusal/çıktısal arayüz.
- Geçici izlerin nedensel takibi ve episode yaşam döngüsü.
- Akson terminalleri ile dendritlerin bağlantı repertuvarı/topolojisi için eşleştirme kuralı.
- Büyük ağlarda kimyasal kaynak sorgusu ve kaynak belleği yaşam döngüsü optimizasyonu.

## Doğrulama durumu

Testler güncellendi:
- `test_orchestration.py`: olay önceliği, entegrasyon tekilleştirme, tam hedefe varış zamanı, refrakter tamponun dinlenmeye dönüşte işlenmesi, olay limiti ve deterministiklik.
- `test_electrical.py`: nöronun yerel entegrasyon/ateşlenme sorumluluğu, faz döngüsü, elektriksel toplama, seçici sinaps aktivasyonu, öğrenme ve sonlu değer doğrulaması.
- `test_chemical.py`: transmitter ayrımı, analitik yayılım, reseptör yanıtı ve geçersiz/sonlu olmayan kaynak-sorgu girdileri.
- `test_microglia.py`: bağımsız mikroglia taraması, algılama yarıçapı, kimyasal budama/stabilizasyon, fiziksel kopma koşulları ve sonlu zaman aralığında periyodik bakım.
- `test_structural_plasticity.py`: yerel büyüme sinyali, hedef dendrit reseptör uygunluğu, uzamsal sınır, deterministik hedef seçimi, tekilleştirme ve zayıf başlangıç.

**Önemli:** Bu çalışma ortamında GitHub dosyaları düzenlenebildi; ancak Python test çalıştırıcısı uzak dalın checkout'una erişmediği için bu dalın testleri burada çalıştırılmış değildir. Testlerin geçtiği iddia edilmiyor. Yerel doğrulama için proje kökünde:

```powershell
python -m pytest BrainNew/tests -v
python -m BrainNew.main
```

Bir test başarısız olursa önce kod hatası, test varsayımı ve açık tasarım kararı birbirinden ayrılmalıdır. Başarısız testi yalnızca yeşile çevirmek için tasarım davranışı değiştirilmemelidir.
