# Yerel Dendrit-Sinaps Dinamikleri — Tasarım

Bu belge `experiment/dendritic-synaptic-potentials` dalındaki yeni mekanizmanın uygulama sözleşmesidir. Mevcut `fix/synaptic-contribution-tracking` dalı değiştirilmez.

## 1. Temel ayrım

Nöronun aksiyon potansiyeli, bütün sinapsların otomatik olarak nörotransmitter salması anlamına gelmez. Aksiyon potansiyeli akson uçlarına ulaşan bir ön-sinyaldir. Her terminal/sinaps kendi yerel durumuna ve eşiğine göre salınım yapıp yapmayacağına karar verir.

Postsinaptik tarafta dendritler pasif toplama noktası değildir. Her dendrit, aynı nörona gelen sinapsların her birinin yerel potansiyelini ayrı katsayılarla etkiler.

## 2. Durum değişkenleri

### Dendrit-sinaps etkileşim matrisi

Her hedef nöron için:
- (W_{ij}): dendrit (i)'nin gelen sinaps (j)'nin yerel potansiyeline katkısı.
- Başlangıçta seed'li rastgele, pozitif ve negatif değerler.
- Başlangıç dağılımı sıfır ortalamalı ve küçük genlikli olmalı; ilk kalibrasyon aralığı ([-0.1, +0.1]).
- Her dendritin aktivitesi yalnızca o zaman adımında matrise katkı verir.

Bir zaman adımında:
[
P_j leftarrow ho P_j + sum_i W_{ij}D_i
]
Burada (P_j) sinapsın yerel potansiyeli, (D_i) dendritin o adımda aldığı yerel etkinlik, (ho) potansiyel sızıntı katsayısıdır.

### Sinapsın bağımsız durumu

Her sinaps:
- yerel potansiyel (P_j),
- salınım eşiği (	heta_j),
- geçici etkinlik izi (T_j),
- son etkinleşme zamanı,
- yapısal dayanıklılık / kullanılmama yaşı
taşır.

Sinaps yalnızca (P_j geq 	heta_j) olduğunda etkinleşir. Eşiği geçmeyen sinapsın akson ucu uyarılmış olsa bile salınım gerçekleşmez.

### Sinaps-sinaps etkileşimi

Başlangıçta sinapslar arası etkileşim matrisi (L_{kj}=0) olur. Aynı nörondaki iki sinaps tekrar tekrar birlikte etkinleştiğinde aralarındaki ilişki küçük adımlarla artar:
[
L_{kj} leftarrow operatorname{clip}(L_{kj} + eta_c C_{kj}, -L_{max}, L_{max})
]
(C_{kj}), iki sinapsın örtüşen geçici etkinlik izidir. İlk sürümde birlikte-etkinleşme pozitif ilişkiyi artırır; işaretin öğretici feedback ile tersine çevrilebilmesi ayrıca test edilir. Böylece sıfır başlangıç, keyfî bir sinaptan-sinapsa bağlantı örüntüsü dayatmaz.

Sinaps (k) etkinleştiğinde (L_{kj}) üzerinden diğer sinapsların potansiyellerine yerel etki aktarılır. Kendine etki ((k=j)) yoktur.

## 3. Geçici iz

Her sinaps etkinleştiğinde (T_j) artar. Zamanla üstel olarak azalır:
[
T_j(t+1)=gamma T_j(t)
]
İz, üç iş için kullanılır:
1. Feedback geldiğinde hangi sinapsların gerçekten etkinleştiğini belirlemek.
2. Birlikte-etkinleşme ilişkisini hesaplamak.
3. Geri bildirim dalgasının önceki yerel adımlarını ayırt etmek.

İz tek başına kalıcı öğrenme değildir; deneme/episode sonunda temizlenebilir. Öğrenilmiş matris ve eşikler korunur.

## 4. Geri bildirim ve yayılım

Feedback doğrudan sinaptik iletim genliğini güncellemez. Öncelikle sinaps eşiklerini ve dendrit-sinaps katsayılarını etkiler.

Bir nörona pozitif feedback ulaştığında:
- izli/etkinleşmiş sinapsların eşiği çok az düşer,
- izsiz/etkinleşmemiş sinapsların eşiği çok az yükselir.

Negatif feedback'te bunun tersi olur.

Her bağlantı/önceki neden adımında etki zayıflar:
[
Delta	heta_j(h)=scdoteta_fcdot r^h
]
- (s=+1): pozitif feedback; etkin sinaps eşiğini düşürür.
- (s=-1): negatif feedback; etkin sinaps eşiğini yükseltir.
- (h): geri yayılım derinliği.
- (0<r<1): her önceki basamakta azalan etki.

İşaret ve etkin/etkin değil eşlemesi ters yönde uygulanır. Feedback dalgası yalnızca geçici iz taşıyan nedensel yollardan geriye yürür; tüm ağı taramaz. Aynı nöron bir dalgada en fazla bir kez işlenir.

Dendrit-sinaps katsayıları da feedback ile güncellenir; yalnızca eşik güncellemesi yeterli değildir. Katsayı güncellemesinde her (W_{ij}) için o dendritin o sinapsın etkinleşmesine katkı izi kullanılır. Böylece kullanıcının ilk fikrindeki asıl öğrenme nesnesi korunur.

## 5. Bağlantı yaşlanması ve budama

Bir bağlantı kullanılmadığı her biyolojik adımda yaşlanır. Kullanıldığında kullanılmama sayacı sıfırlanır. Dayanıklılık kademeli azalır; sabit bir yaş eşiği veya dayanıklılık alt sınırı aşıldığında bağlantı kopar. Yaşlanma:
- bir anda silme şeklinde değil, kademeli olmalı,
- aktif bağlantıların ömrünü uzatmalı,
- yalnızca bir denemede kullanılmadı diye bağlantıyı silmemeli,
- parametreleri simülasyon adımıyla ölçeklenmeli.

İlk kalibrasyonda dayanıklılık `1.0`, her kullanılmama adımında çarpan `0.9995`, kopma sınırı `0.1` önerilir. Bu yaklaşık 4,600 kullanılmama adımında kopma demektir; gerçek süre deney sonuçlarına göre ayarlanır.

## 6. Yeni bağlantı oluşumu

Ateşlenen nöronun bağlı olmayan akson terminali etkinleşme girişiminde bulunursa, bu olay bir büyüme adayı kaydı oluşturur; bağlantı otomatik ve koşulsuz kurulmaz. Pozitif feedback geldiğinde aday terminalden yerel bir dendrite yeni bağlantı kurulabilir. Negatif feedback adayın oluşmasını veya kalıcılığını desteklemez.

Yeni bağlantının başlangıç eşiği ve dendrit-sinaps katsayısı küçük/kararsız başlar; tekrar kullanım ve olumlu yerel feedback ile yerleşir. Hedef dendrit rastgele tüm ağdan seçilmez; büyüme yalnızca ilgili yerel hedef nöron/izin verilen komşuluk içinden yapılır.

## 7. Başlangıç parametreleri ve kalibrasyon

İlk denemede:
- (W_{ij}): seed'li uniform ([-0.1, +0.1])
- (L_{kj}): sıfır
- (	heta_j): seed'li dar dağılım; önerilen ilk aralık ([0.2, 0.4]) normalize potansiyel birimi
- potansiyel sızıntısı: her adımda küçük, sabit oran
- etkinlik izi: her adımda üstel sönüm
- feedback derinlik çarpanı (r): ilk deneme için (0.5)
- feedback başına eşik değişimi: başlangıçta küçük; eşik pozitif alt sınırla korunur.

Bu sayılar biyolojik sabitler değildir. Ölçeksiz/normalize prototip parametreleridir. Başlangıç testleri her sinapsı tek tek, iki dendriti eşzamanlı ve çoklu dendrit kombinasyonlarını ayrı ayrı sınamalıdır. Parametreler eğitim başarısına göre değil, önce deterministik yerel davranış testlerine göre kalibre edilir.

## 8. Zorunlu testler

1. Bir dendritin katsayısı yalnızca hedeflediği sinaps potansiyelini değiştirir.
2. Aynı anda D1, D3, D4 aktifken S1 ve S2'nin bağımsız eşik davranışı doğrulanır.
3. Nöron spike'ı bütün sinapsları zorunlu çalıştırmaz.
4. Bir sinapsın çalışması diğer sinapsları (L) üzerinden etkiler.
5. Sıfır (L) başlangıcı, birlikte etkinleşme olmadan sinapslar arası etki üretmez.
6. Pozitif ve negatif feedback eşikleri ters yönde günceller.
7. Feedback etkisi her geri adımda azalır.
8. Geçici iz zamanla kaybolur; episode resetinde temizlenir.
9. Kullanılmayan bağlantı yaşlanır; tekrar kullanılan bağlantının yaşı sıfırlanır.
10. Bağlı olmayan akson terminalinin etkinleşme girişimi büyüme adayı oluşturur; pozitif feedback ile bağlantı kurulur.
11. Seed aynıysa başlangıç matrisi ve deney sonuçları tekrarlanabilir.
12. Öğrenilmiş (W), (L), eşikler ve yapısal bağlantılar denemeler arasında korunur.

## 9. Açık araştırma noktaları

- Birlikte etkinleşme, sinapslar arası ilişkiyi hangi koşulda artırmalı: aynı zaman adımı mı, zaman penceresi mi?
- Sinapslar arası etki başlangıçta pozitif mi kalmalı, yoksa feedback ile negatif ilişki de öğrenebilmeli mi?
- Dendritin sinaps üzerindeki etkisi doğrudan potansiyel değişimi mi, yoksa eşik/iletim olasılığı modülasyonu mu olmalı?
- Akson terminali etkinleşmesi ile postsinaptik sinapsın salınım kararı arasındaki zamanlama nasıl modellenmeli?
- Sinapsın kendi potansiyeli ve bağlantının yapısal dayanıklılığı birbirinden ayrı tutulmalı.

Bu belgenin kapsamı tasarım sözleşmesidir; henüz çalışan entegrasyon veya test başarısı iddiası değildir.
