# BrainNew — Deney ve Ölçüm Protokolü

Durum: Aşama 2 tasarım sözleşmesi.
Bağlı belgeler: `LEARNING_SPRINT.md`, `LEARNING_ARCHITECTURE_AUDIT.md`.

Bu protokol, öğrenme mekanizmalarının gerçekten görev başarısı üretip üretmediğini ölçmek içindir. Gözlem/ölçüm katmanı öğrenmeye müdahale etmez; ağırlık değiştirmez, sinaps seçmez, geri bildirim üretmez.

## 1. Deney yürütme sözleşmesi

Her deney; deney kimliği ve sürümü, başlangıç ağının/topolojinin özeti, rastgelelik tohumu, simülasyon zamanı, eğitim ve test görevleri, tekrar sayısı, etkin/kapalı mekanizmalar, sayısal parametreler, sonuç ölçütleri ve olay sayımlarını kaydeder. Yapılandırmanın değişmez anlık görüntüsü her koşuyla saklanır.

## 2. Determinizm

Rastgelelik kullanılmıyorsa `seed=null` kaydedilir. Rastgele başlangıç/topoloji/örnek sıralaması eklendiğinde seed alt bileşenlere kararlı biçimde türetilir. Aynı kod, yapılandırma, başlangıç durumu ve seed aynı eğitim sırasını, olay sırasını, ölçüm zamanlarını ve sonuçları üretmelidir. Determinizm yalnızca ateşlenme sayısını değil, olay ve öğrenilmiş parametre izlerini karşılaştırır.

## 3. Olay kayıtları

Her kayıt simülasyon zamanı, monoton olay sıra numarası, olay türü, kaynak/hedef kimlikleri ve ilgili yerel değişimleri taşır. Gerekli türler: duyusal/sinaptik girdi, entegrasyon, aksiyon potansiyeli ve faz geçişi, terminal aktivasyonu, transmitter salımı, dendritik yanıt, pre/post iz güncellemesi, uygunluk izi, kalıcı ağırlık değişimi, dendrit-terminal katkı değişimi, modülatör maruziyeti, homeostatik güncelleme, bakım değerlendirmesi ve bağlantı oluşumu/kopması. Her olayda bütün ağın kopyası tutulmaz.

## 4. Ölçüm değişkenleri

### Davranış
- doğru yanıt, yanlış pozitif ve yanlış negatif oranları;
- A→B / B→A sıralama ayrımı;
- örüntü tamamlama;
- eğitim ve test performansı farkı;
- yeni öğrenme sonrası eski görev performansındaki değişim.

### Nöral
- nöron başına ateşlenme sayısı/oranı;
- sessiz ve aşırı etkin nöron oranı;
- membran durumu;
- ilgili ayrım tanımlandığında uyarıcı/baskılayıcı yanıt dengesi.

### Sinaptik
- kalıcı sinaptik etkinlik katsayısı;
- geçici terminal hazır olma potansiyeli;
- dendrit-terminal katkısı;
- presinaptik ve postsinaptik kısa ömürlü etkinlik izleri;
- uygunluk izi (henüz uygulanmadı);
- ağırlık sınırına dayanmış sinaps oranı;
- etkinleşme ve bağlantı yaşam süresi dağılımı.

Bu değişkenler birbirinin yerine kullanılamaz. Terminal hazır olma potansiyelinin artması kalıcı sinaptik öğrenme sayılmaz.

### Kimyasal
- transmitter türü başına kaynak sayısı;
- hedef konumlarda yoğunluk-zaman eğrisi;
- modülatörün yerel maruziyet integrali;
- reseptör profiline göre yerel yanıt;
- aynı kimyasal kaynağın yinelenen sorgularla yanlışlıkla tekrar öğrenme üretip üretmediği.

## 5. Baseline görev ailesi

Öğrenme eklenmeden önce rastgele/başlangıç ağının başarısı ölçülür. Amaç başlangıçta başarılı olmasını beklemek değil, karşılaştırma noktası oluşturmaktır.

- **B1 Tek örüntü çağırma:** Bir girdi örüntüsüne atanmış yanıtı eğitim sonrasında yeniden üretme.
- **B2 İki örüntüyü ayırt etme:** En az bir bileşenle ayrılan iki örüntüye farklı yanıtlar atama.
- **B3 Zamansal sıra ayrımı:** A→B ve B→A dizileri farklı hedeflerle eşleşir; toplam bileşen ve tekrar sayıları eşit tutulur.
- **B4 Gürültüye dayanıklılık:** Öğrenilmiş örüntünün bir kısmı değiştirilir, çıkarılır veya gürültülenir.
- **B5 Kısmi ipucundan tamamlama:** Örüntünün alt kümesi sunulur; kalan yapıyı geri çağırma ölçülür.
- **B6 Genelleme:** Eğitimde görülmeyen örnekler aynı yapısal kuralı taşır; ezber yerine ortak ilişkiyi kullanma ölçülür.

Görev tanımları sabitlenmeden algoritma başarıya göre ayarlanamaz. Test örnekleri eğitim sırasında ağa verilmez.

## 6. Karşılaştırma düzeni

Her katman için en az üç koşul: (1) öğrenme kapalı baseline, (2) yalnızca ilgili katman açık, (3) önceki kabul edilmiş katmanlar ve yeni katman açık. Katmanın katkısı beklenen özgül görevde ölçülür. STDP için A→B/B→A ayrımı; üç faktörlü öğrenme için gecikmiş modülatörün uygunluk izi taşıyan bağlantılarda seçici değişim üretmesi temel ölçüttür.

## 7. İstatistiksel raporlama

Tek başarılı koşu yeterli değildir. İlk deterministik testlerde tek seed davranış doğrulaması içindir; genelleme iddiası için birden fazla seed gerekir. Seed ve örnek sayısı belirtilir; ortalama yanında dağılım ve uç koşular raporlanır. Eğitim/test ayrı tutulur. Hiperparametre ayarı test kümesinde yapılmaz; ayrı doğrulama kümesi kullanılır.

## 8. Ölçüm altyapısı kabul kapısı

1. Deney yapılandırması tekrar üretilebilir.
2. Olay günlüğü olay sırasını bozmaz.
3. Kayıt sistemi simülasyon durumunu değiştirmez.
4. Aynı koşu iki kez aynı ölçüm çıktısını üretir.
5. Davranış ölçütleri öğrenme parametrelerinden bağımsız hesaplanır.
6. Eğitim/test örnekleri ayrıdır.
7. Başlangıç ağının B1–B6 sonuçları kaydedilir.

## 9. İlk uygulama sınırı

İlk kodlama adımında yalnızca yan etkisiz deney kayıt katmanı eklenir. Öğrenme kuralları, sinaps davranışı, ateşleme eşiği, kimyasal yayılım veya olay zamanlaması değiştirilmez. Gözlemci Beyin'in olay kuyruğuna müdahale etmez. Kayıt kapalıyken mevcut davranışla aynı sonuç alınmalıdır.


## Pasif aktivasyon izi ve deney snapshot'ları

- ActivationTrace, Beyin(aktivasyon_izi=ActivationTrace()) ile isteğe bağlı bağlanır.
- Olay kuyruğundan çıkan olayları, nöron ateşlenmelerini, ateşlenmede seçilmiş çıkış sinapslarını ve terminalin anlık elektriksel durumunu kaydeder.
- nedensel_yol(noron_id), izleyicinin açık olduğu sırada gözlenen son ateşlenmeye doğru sinaptik aktivasyonları geriye izler. İzleyici başlamadan önceki geçmişi veya kaydedilmemiş olayları yeniden kuramaz.
- İzleyici salt okunurdur; öğrenme, eşik, ağırlık, olay zamanlaması veya sinaps seçimini değiştirmez.
- Örnek:
  ```python
  from BrainNew.ActivationTrace import ActivationTrace
  from BrainNew.Beyin import Beyin

  iz = ActivationTrace()
  beyin = Beyin(aktivasyon_izi=iz)
  # Ağı kur ve deneyi çalıştır.
  beyin.calistir()
  print(iz.ozet())
  print(iz.nedensel_yol("hedef_noron"))
  ```
- Tam beyin snapshot kaydetme/yükleme ayrı tasarım planındadır; şu an mevcut değildir. Deney karşılaştırmalarında mevcut ağ kurucusunun seed'i, tüm deney parametreleri ve ölçüm çıktıları ayrıca kaydedilmelidir.
