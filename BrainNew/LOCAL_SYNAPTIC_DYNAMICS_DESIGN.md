# Yerel Dendrit-Sinaps Dinamikleri — Tasarım

Bu belge `experiment/dendritic-synaptic-potentials` dalındaki sıfırdan başlatılan yeni BrainNew tasarımının uygulama sözleşmesidir. Eski `fix/synaptic-contribution-tracking` dalı bu tasarımın çalışma dalı değildir.

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

\[
P_j \leftarrow \rho P_j + \sum_i W_{ij}D_i
\]

Burada (P_j) sinapsın yerel potansiyeli, (D_i) dendritin o adımda aldığı yerel etkinlik, (\rho) potansiyel sızıntı katsayısıdır.

### Sinapsın bağımsız durumu

Her sinaps:
- yerel potansiyel (P_j),
- salınım eşiği (\theta_j),
- geçici etkinlik izi (T_j),
- son etkinleşme zamanı,
- yapısal dayanıklılık / kullanılmama yaşı
taşır.

Sinaps yalnızca (P_j \geq \theta_j) olduğunda etkinleşir. Eşiği geçmeyen sinapsın akson ucu uyarılmış olsa bile salınım gerçekleşmez.

### Sinaps-sinaps etkileşimi

Başlangıçta sinapslar arası etkileşim matrisi (L_{kj}=0) olur. Aynı nörondaki iki sinaps tekrar tekrar birlikte etkinleştiğinde aralarındaki ilişki küçük adımlarla artar:

\[
L_{kj} \leftarrow \operatorname{clip}(L_{kj} + \eta_c C_{kj}, -L_{max}, L_{max})
\]

(C_{kj}), iki sinapsın örtüşen geçici etkinlik izidir. İlk sürümde birlikte-etkinleşme pozitif ilişkiyi artırır; işaretin öğretici feedback ile tersine çevrilebilmesi ayrıca test edilir. Böylece sıfır başlangıç, keyfî bir sinaptan-sinapsa bağlantı örüntüsü dayatmaz.

Sinaps (k) etkinleştiğinde (L_{kj}) üzerinden diğer sinapsların potansiyellerine yerel etki aktarılır. Kendine etki ((k=j)) yoktur.

## 3. Geçici iz

Her sinaps etkinleştiğinde (T_j) artar. Zamanla üstel olarak azalır:

\[
T_j(t+1)=\gamma T_j(t)
\]

İz, kısa süreli yerel etkinlik geçmişini taşır ve şu işlerde kullanılır:
1. Feedback geldiğinde hangi yerel konumların etkin/etkin değil olduğunu belirlemek.
2. Birlikte-etkinleşme ilişkisini hesaplamak.
3. Feedback'in geriye doğru hangi dallardan ilerleyebileceğini, güncel adım verileriyle birlikte belirlemek.

Feedback için ayrıca kalıcı bir nedensel yol/iz (track) veri yapısı tutulmayacaktır. Geriye dönük erişim, geçici etkinlik izleri ve güncel adım verileri üzerinden sağlanır. Dolayısıyla ayrı bir track bulunmaması geçmiş bilgisinin hiç bulunmadığı anlamına gelmez; bu bilgi kısa ömürlü yerel izlerde taşınır.

İz tek başına kalıcı öğrenme değildir; deneme/episode sonunda temizlenebilir. Öğrenilmiş matris ve eşikler korunur.

## 4. Geri bildirim ve yayılım

Feedback, yalnızca tek bir merkezi yol kaydını izlemek yerine, yerel etkinlik izleri ve güncel adım verileri üzerinden geriye doğru takip edilebilen bütün dallara yayılabilir. Her dal kendi iz değerine göre bağımsız değerlendirilir.

Bir dalda geri yayılım, o dalın etkinlik izi ilgili geri-adım eşiğinin altına düştüğünde durur. Eşik geri gidilen adım sayısına göre değişebilir. Bir dalın durması diğer dalların ilerlemesini durdurmaz. Sabit bir maksimum derinlik, temel durdurma kuralı değildir; yayılımın sınırını dal bazındaki iz eşiği belirler.

Geri bildirim ulaştığı her konumda etkinlik potansiyeline küçük bir ekleme veya çıkarma yapar. Geriye doğru her adımda etkinin büyüklüğü azalır. Etkinin sayısal katsayıları ve adım başına azalma miktarı henüz kalibre edilmemiştir.

Aynı geri bildirim dalgası içinde aynı yerel konuma birden fazla daldan etki ulaşırsa, bu katkılar o konum için birleştirilir ve tek bir birleşik etki olarak uygulanır. Birleştirme nöronun tamamında değil, etkilenen yerel eleman/konum bazında yapılır; farklı yerel konumlar bağımsız kalır.

Birleşik etkinin uygulanacak büyüklüğü sabit bir etki tavanıyla değil, hedef elemanın mevcut aktiflik potansiyelinin izin verilen aralığın sınırlarına yakınlığıyla belirlenir. Potansiyel ilgili yöndeki sınıra yaklaştıkça o yönde uygulanabilecek etki giderek zayıflar ve sınıra ulaşıldığında sıfıra yaklaşır. Böylece pozitif ve negatif katkılar birbirini dengeleyebilir; ancak kararlılık yalnızca bu nötralizasyona bırakılmaz.

İlk matematiksel öneri, potansiyel aralığı \([P_{min}, P_{max}]\) için şöyledir. Önce aynı konuma gelen katkılar toplanır: \(\Delta P = \sum_i \Delta P_i\). Ardından:
\[
\Delta P_{\text{uyg}} =
\begin{cases}
\Delta P \cdot \dfrac{P_{max}-P}{P_{max}-P_{min}}, & \Delta P > 0 \\
\Delta P \cdot \dfrac{P-P_{min}}{P_{max}-P_{min}}, & \Delta P < 0 \\
0, & \Delta P = 0
\end{cases}
\]
Burada \(P\), etki uygulanmadan önce hedef elemanın mevcut aktiflik potansiyelidir. Bu ölçekleme pozitif ve negatif yönlerde ayrı ayrı yakınsama sağlar. Doğrusal ölçekleme şu an kabul edilen ilk modeldir; üstel veya başka bir yakınsama eğrisiyle karşılaştırılması daha sonraki deney konusudur. \(P_{min}\) ve \(P_{max}\) değerleri henüz belirlenmemiştir.

Etkinlik izi bulunan ve bulunmayan konumlara uygulanacak etki:

| Feedback türü | Etkinlik izi bulunan konum | Etkinlik izi bulunmayan konum |
|---|---|---|
| Pozitif | Küçük kolaylaştırıcı etki | Çok küçük engelleyici etki |
| Negatif | Küçük engelleyici etki | Kolaylaştırıcı etki |

Negatif feedback, pozitif feedback tablosunun tam tersini uygular. Buradaki kolaylaştırma/engelleme, etkinlik potansiyeline yapılan küçük yerel etkiyi ifade eder; tek başına belirli bir sinaptik parametrenin kesin olarak artırılıp azaltıldığı anlamına gelmez.

Feedback'in dendrit-sinaps katsayılarını (W_{ij}) ve sinaps eşiklerini nasıl güncelleyeceği, yukarıdaki yerel potansiyel etkisinden ayrı bir parametre-güncelleme kuralı olarak ele alınmalıdır. Önceki taslaktaki eşik ve katsayı güncelleme yönleri, bu yeni feedback davranışından otomatik olarak çıkarılmış kesin kararlar sayılmaz; ayrıca netleştirilmelidir.

Beyin feedback'in içeriğine veya hangi sinapsların değişeceğine karar vermez. Beyin yalnızca simülasyon zamanını ve bileşenler arası koordinasyonu yönetir; feedback'in yerel değerlendirilmesi ve öğrenme kararları nöronlar/yerel mekanizmalar tarafından yapılır.

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
- (\theta_j): seed'li dar dağılım; önerilen ilk aralık ([0.2, 0.4]) normalize potansiyel birimi
- potansiyel sızıntısı: her adımda küçük, sabit oran
- etkinlik izi: her adımda üstel sönüm
- feedback'in geriye doğru adımlarda azalma katsayısı: henüz belirlenmedi
- feedback başına yerel potansiyel değişimi: küçük olmalı; sayısal değer henüz belirlenmedi.

Bu sayılar biyolojik sabitler değildir. Ölçeksiz/normalize prototip parametreleridir. Başlangıç testleri her sinapsı tek tek, iki dendriti eşzamanlı ve çoklu dendrit kombinasyonlarını ayrı ayrı sınamalıdır. Parametreler eğitim başarısına göre değil, önce deterministik yerel davranış testlerine göre kalibre edilir.

## 8. Zorunlu testler

1. Bir dendritin katsayısı yalnızca hedeflediği sinaps potansiyelini değiştirir.
2. Aynı anda D1, D3, D4 aktifken S1 ve S2'nin bağımsız eşik davranışı doğrulanır.
3. Nöron spike'ı bütün sinapsları zorunlu çalıştırmaz.
4. Bir sinapsın çalışması diğer sinapsları (L) üzerinden etkiler.
5. Sıfır (L) başlangıcı, birlikte etkinleşme olmadan sinapslar arası etki üretmez.
6. Pozitif ve negatif feedback'in etkin ve etkin olmayan izlere etkileri tabloda belirtilen şekilde ters yönlüdür.
7. Feedback geriye doğru bütün erişilebilir dalları ayrı ayrı izler; bir dalın kesilmesi diğer dalları durdurmaz.
8. Her dalın yayılımı kendi etkinlik izinin adım sayısına bağlı eşiğin altına düşmesiyle durur.
9. Feedback etkisi geriye doğru her adımda azalır.
10. Aynı geri bildirim dalgasında aynı yerel konuma farklı dallardan gelen katkılar birleştirilerek tek etki olarak uygulanır; farklı yerel konumlar birbirinden bağımsız kalır.
11. Geri bildirim etkisinin uygulanabilir büyüklüğü hedef elemanın mevcut aktiflik potansiyeline göre ölçeklenir; potansiyel ilgili sınıra yaklaştıkça etki sıfıra yaklaşır ve izin verilen aralık aşılmaz.
10. Geçici iz zamanla kaybolur; episode resetinde temizlenebilir.
11. Feedback yayılımı için ayrıca kalıcı bir track veri yapısı tutulmaz.
12. Kullanılmayan bağlantı yaşlanır; tekrar kullanılan bağlantının yaşı sıfırlanır.
13. Bağlı olmayan akson terminalinin etkinleşme girişimi büyüme adayı oluşturur; pozitif feedback ile bağlantı kurulur.
14. Seed aynıysa başlangıç matrisi ve deney sonuçları tekrarlanabilir.
15. Öğrenilmiş (W), (L), eşikler ve yapısal bağlantılar denemeler arasında korunur.

## 9. Açık araştırma noktaları

- Birlikte etkinleşme, sinapslar arası ilişkiyi hangi koşulda artırmalı: aynı zaman adımı mı, zaman penceresi mi?
- Sinapslar arası etki başlangıçta pozitif mi kalmalı, yoksa feedback ile negatif ilişki de öğrenebilmeli mi?
- Dendritin sinaps üzerindeki etkisi doğrudan potansiyel değişimi mi, yoksa eşik/iletim olasılığı modülasyonu mu olmalı?
- Akson terminali etkinleşmesi ile postsinaptik sinapsın salınım kararı arasındaki zamanlama nasıl modellenmeli?
- Sinapsın kendi potansiyeli ve bağlantının yapısal dayanıklılığı birbirinden ayrı tutulmalı.
- Feedback'in yerel etkinlik potansiyelini değiştirmesi ile öğrenilmiş parametreleri (eşikler, dendrit-sinaps katsayıları vb.) güncellemesi arasındaki kesin ilişki nasıl kurulmalı?
- Dallar için adım sayısına bağlı iz eşiğinin matematiksel biçimi ne olmalı?
- Aynı geri yayılım dalında birden fazla iz/konum bulunursa dallanma ve tekrar ziyaret nasıl ele alınmalı?

Bu belgenin kapsamı tasarım sözleşmesidir; henüz çalışan entegrasyon veya test başarısı iddiası değildir.
