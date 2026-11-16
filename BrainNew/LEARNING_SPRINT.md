# BrainNew — Öğrenme Yeteneği Sprinti (Teorik Tasarım)

Durum: **Aşamalı uygulama sürüyor**  
Çalışma dalı: `fix/brainnew-architecture-audit`

Bu sprintin hedefi BrainNew'i yalnızca sinyal ileten ve birkaç yerel parametresi değişen bir ağ olmaktan çıkarıp, deneyimden kalıcı ve seçici biçimde öğrenebilen bir sisteme dönüştürmek için gereken teorik mimariyi tamamlamaktır. Sprint tek bir bütün olarak yürütülür; fakat her adımın kendi kabul ölçütü vardır. Bir adım kabul edilmeden sonraki adıma geçilmez.

Bu belge bir biyolojik beyin simülasyonunun tamamlandığını veya aşağıdaki kuralların biyolojik olarak birebir doğru olduğunu iddia etmez. Amaç, biyolojiden esinlenen, matematiksel olarak tanımlı, test edilebilir ve öğrenme başarısı ölçülebilir bir hesaplamalı model kurmaktır.

---

## Güncel yürütme durumu

- **Aşama 1 — teorik veri/topoloji denetimi:** tamamlandı. Ayrıntı: `LEARNING_ARCHITECTURE_AUDIT.md`.
- **Aşama 2 — deney ve ölçüm protokolü:** tasarlandı ve ilk pasif olay kaydedicisi uygulandı. Ayrıntı: `LEARNING_EXPERIMENT_PROTOCOL.md`, `DeneyKaydi.py`.
- **Aşama 2 — deney ve ölçüm altyapısı:** pasif olay kaydı ve deterministik baseline yürütücüsü eklendi. Baseline yürütücüsü örnek başına bağımsız ağ kurar; eğitim/test örneklerini kimlik düzeyinde ayırır; tam eşleşme, doğru pozitif, yanlış pozitif ve yanlış negatif ölçer.
- **Aşama 2 doğrulaması:** kullanıcı mevcut testlerin ve prototip smoke testinin başarılı olduğunu bildirdi. Baseline yürütücüsüne ait yeni testler bu son commit'te eklendi; henüz kullanıcı ortamında çalıştırılmadı.
- **Aşama 3 — baseline yürütücü:** genel örnek/görev ölçüm altyapısı kodlandı. Kullanıcı mevcut testlerin ve prototip smoke testinin başarılı olduğunu bildirdi; yeni baseline yürütücü testlerinin son commit sonrası tekrar çalıştırılması gerekiyor.
- **Aşama 4 — kısa ömürlü etkinlik izleri:** ilk uygulama eklendi. Her bağlantıda ayrı presinaptik ve postsinaptik iz, bağımsız üstel sönüm ve hedef nöronun yerel ateşlenmesiyle postsinaptik iz güncellemesi var. İzler henüz kalıcı sinaptik ağırlığı değiştirmiyor; bu ayrım korunuyor. Yeni iz testleri son commit sonrası henüz çalıştırılmadı.
- **Önemli:** Kalıcı gerçek sinaptik etkinlik katsayısı, pre/post izleri, uygunluk izi ve plastisite kuralları henüz kodda yoktur.

---

## 0. Sprintin başarı tanımı

Sprint sonunda sistemin teorik olarak şu davranışları gösterebilmesi gerekir:

1. Tekrarlanan deneyimlerden yerel ilişkiler öğrenebilmesi.
2. Zamansal sırayı öğrenebilmesi; A ardından B ile B ardından A'yı ayırt edebilmesi.
3. Öğrenmenin yalnızca eşzamanlı ateşlenme sayımına indirgenmemesi.
4. Gecikmiş geri bildirimin, yakın geçmişte etkin olmuş doğru sinapslarda kalıcı değişim oluşturabilmesi.
5. Kullanışlı bağlantıları korurken gereksiz/zayıf bağlantıları zamanla zayıflatabilmesi.
6. Sürekli öğrenirken ağın kontrolsüz biçimde doygunlaşmaması veya tüm etkinliğini kaybetmemesi.
7. Öğrenilmiş örüntüyü kısmi, gürültülü veya eksik girdiden yeniden çağırabilmesi.
8. Daha önce görülmemiş örneklerde öğrendiği ilişkinin bir kısmını genelleyebilmesi.
9. Öğrenme kararlarının sinaps, dendrit ve nöronların yerel mekanizmalarından çıkması; Beyin'in yalnızca olay ve zaman koordinasyonu yapması.
10. Aynı başlangıç koşulu ve rastgelelik tohumu altında tekrarlanabilir sonuç vermesi.

**Önemli sınır:** Sadece Hebb/STDP ile bütün bu başarılar garanti edilemez. Korelasyon temelli yerel öğrenme örüntü ve zaman ilişkilerini keşfedebilir; ancak hangi değişimin bir hedefe/sonuca yararlı olduğunu kendi başına her durumda bilemez. Bu nedenle yerel uygunluk izi ve yerel modülatör/geri bildirim katmanı gerekir. Öğrenmenin kapsamı, kullanılan geri bildirim türüyle açıkça sınırlandırılacaktır.

---

## 1. Sabit mimari ilkeler

- Beyin yalnızca simülasyon zamanını, olay kuyruğunu ve bileşenler arası koordinasyonu yönetir.
- Beyin kayıp/ödül hesaplayıp sinaps seçmez; hangi bağlantının değişeceğine karar vermez.
- Sinaps kendi etkinlik geçmişini, uygunluk izini, yerel kimyasal maruziyetini ve yapısal durumunu tutar.
- Dendrit yerel girdileri, reseptör yanıtını ve kendi yerel öğrenilmiş katkılarını değerlendirir.
- Nöron ateşlenme, yerel etkinlik ve kendi durum geçişlerini yönetir.
- Mikroglia-benzeri bakım/budama davranışı bağlantı nesnesinin yerel kural kümesiyle temsil edilir. Bu, gerçek mikroglianın sinapsın içine gömülü olduğu iddiası değildir.
- Bütün ağın her adımda taranması ve yoğun tüm-çift matrisler temel yöntem olmayacaktır.
- Geçici aktivite izleri, kalıcı öğrenilmiş ağırlıklar ve yapısal bağlantı durumu ayrı tutulur.
- Öğrenme güncellemeleri sınırlı, deterministik, olay-tabanlı ve test edilebilir olmalıdır.

## 2. Öğrenme katmanları

Öğrenme tek bir formül olmayacak. Farklı zaman ölçeklerinde çalışan beş katman bulunacak.

### L1 — Yerel ilişki öğrenmesi (Hebbian / korelasyon)

Amaç: Birlikte veya anlamlı biçimde ilişkili etkinliklerin yerel bağlantı/katkı değerlerinde iz bırakması.

- Presinaptik aktivite ve postsinaptik dendrit yanıtı ayrı olaylar olarak kaydedilir.
- Yalnızca aynı zaman penceresinde gerçekleşmeleri değil, işaretli ve zamansal ilişkileri değerlendirilir.
- Güçlenme ve zayıflama ayrı koşullara sahip olur.
- Hiç etkinleşmemiş bağlantı, sırf başka bağlantılar etkinleşti diye cezalandırılmaz.
- Yerel katkı değerleri sınırlandırılır; doygunlukta güncelleme doğal olarak küçülür.
- Hebbian güncelleme kendi başına “bu sonuç iyi miydi?” sorusunu cevaplamaz.

İlk matematiksel aday, sinapsın yerel pre/post etkinlik izlerinin çarpımına dayalıdır:

`H_{ij}(t) = x_i^{pre}(t) \cdot x_j^{post}(t)`

`Δw_{ij}^{Hebb} = η_H · H_{ij}(t)`

Burada izler anlık spike değil, zamanla sönümlenen yerel etkinlik değişkenleridir. İşaret, zaman penceresi ve normalizasyon sonraki testlerde kalibre edilir. Bu formül tek başına nihai öğrenme kuralı değildir.

### L2 — Zamansal öğrenme (STDP benzeri)

Amaç: A→B ve B→A sıralarını ayırt etmek.

- Presinaptik ve postsinaptik olay zamanları bağlantı üzerinde tutulur.
- Zaman farkı `Δt = t_post - t_pre` olarak tanımlanır.
- Zaman farkının işareti ve büyüklüğü güncellemenin işaretini/büyüklüğünü belirler.
- Etki zaman farkıyla üstel biçimde azalabilir; zaman penceresi dışında güncelleme yapılmaz.
- Tek bir spike çiftiyle büyük kalıcı değişim yapılmaz; küçük değişimler tekrarlarla birikir.
- STDP penceresi biyolojik olarak evrensel sabit değildir; simülasyon zaman birimi ve görev ölçeğine göre kalibre edilir.

Başlangıç adayı:

`Δw = A_+ exp(-Δt/τ_+)  if Δt > 0`

`Δw = -A_- exp(Δt/τ_-) if Δt < 0`

Bu kuralın hangi sinaps tiplerinde kullanılacağı ve toplam ağırlık dengesi ayrıca belirlenir. STDP, gecikmiş görev sonucunu tek başına çözmez.

### L3 — Uygunluk izi + yerel modülatör (üç faktörlü öğrenme)

Amaç: Etkinlik ile sonucu birbirinden zaman bakımından ayrılmış olsa bile doğru bağlantıların pekişmesini sağlamak.

Her bağlantı geçici bir uygunluk izi taşır:

`de_{ij}/dt = -e_{ij}/τ_e + F(pre, post, dendritic_state)`

- Yerel pre/post etkinlik ve dendritik durum, uygunluk izini oluşturur.
- İz anında kalıcı ağırlığı değiştirmek zorunda değildir.
- Sonradan gelen yerel modülatör sinyal `M(x,t)`, o bölgede hâlâ uygunluk izi taşıyan bağlantılarda değişimi kapılar.
- Kalıcı değişim adayı:

`Δw_{ij} = η_M · e_{ij} · M(x_{ij},t)`

- `M>0` güçlenmeyi, `M<0` zayıflamayı destekleyebilir; `M≈0` ise uygunluk izi kalıcı değişime çevrilmez.
- Modülatör bütün ağı doğrudan değiştirmez; yalnızca kendi uzamsal/zamansal etkisi içindeki uygun bağlantılar yerel olarak yanıt verir.
- Beyin modülatörün anlamını yorumlamaz ve bağlantı seçmez. Kimyasal alan yalnızca sinyali taşır; bağlantının reseptör/duyarlılık profili yanıtı belirler.

Bu katman, mevcut yerel feedback fikriyle uyumlu biçimde kurulacaktır. Haricî bir görev ortamı ödül/başarı/uyarı sinyali üretebilir; ancak bu sinyal Beyin'e “şu sinapsı değiştir” komutu vermez. Sinyal, normal duyusal/kimyasal yollarla ağa girer ve yerel mekanizmalar tarafından yorumlanır.

### L4 — Homeostatik dengeleme ve metaplastisite

Amaç: Öğrenme sırasında etkinliğin patlayarak artmasını veya sönmesini engellemek; öğrenme eşiğini geçmiş etkinlik düzeyine göre ayarlamak.

- Hebbian/STDP güçlenmesi yerel ve seçici kalır.
- Daha yavaş homeostatik süreçler nöronun uzun dönem ateşlenme oranını izler.
- Nöron aşırı etkinse genel kazanç/uyarılabilirlik veya sinaptik ölçek yavaşça aşağı çekilebilir.
- Nöron uzun süre yetersiz etkinse duyarlılık/ölçek kontrollü biçimde artabilir.
- Homeostatik değişim tek bir öğrenilmiş bağlantıyı rastgele silmez; yerel öğrenilmiş örüntüleri koruyacak biçimde sınırlanır.
- Plastisite eşiği de uzun dönem etkinliğe göre kayabilir (metaplastisite). Böylece aynı etkinlik her koşulda aynı büyüklükte öğrenme üretmez.
- Hızlı ilişki öğrenmesi ile yavaş dengeleme farklı zaman sabitlerine sahip olmalıdır.

İlk sürümde homeostaz nöron düzeyinde düşük boyutlu bir etkinlik hedefi üzerinden modellenebilir. Bu hedef ve zaman sabiti kalibrasyon parametresidir; biyolojik sabit değildir.

### L5 — Yapısal plastisite: bakım, budama ve yeni bağlantı

Amaç: Ağın yalnızca mevcut ağırlıkları değiştirmesi değil, gerektiğinde bağlantı yapısını da değiştirmesi.

- Bağlantı bakımı kaynak nöron entegrasyonundan bağımsız zamanlanır.
- Her bağlantı kendi bakım aralığını ve bir sonraki değerlendirme zamanını belirler.
- Beyin yalnızca bakım olayını olay kuyruğuna koyar.
- Kullanım izi zamanla azalır; kullanım izi tek başına kopma kararı değildir.
- Uzun süre düşük kullanım/zayıf işlev ve yerel budama işaretleri birlikteyse bağlantı önce zayıflamaya, sonra kopmaya aday olur.
- Stabilizasyon/büyüme işaretleri bakım/budama baskısını azaltabilir.
- Kopmuş bağlantı onarılmış gibi davranmaz. Yeni bağlantı oluşumu ayrı bir süreçtir.
- Bağlantısız terminal yalnızca 2B yerel aramayla uygun dendrit adaylarını değerlendirir.
- Yeni bağlantı zayıf başlar; etkinlik, uygun kimyasal sinyaller ve stabilizasyonla olgunlaşır.
- Tek bağlantı kaybı nöronu sıfırlamaz; bütün kullanılabilir çıkış bağlantılarını kaybetme ayrı toparlanma durumudur.

---

## 3. Öğrenme verisinin ve topolojinin doğru tanımı — kritik bağımlılık

Mevcut tasarımda dendritlerin `sinaps_katkilari` üzerinden aynı nöronun çıkış sinapslarını hazırlaması hesaplamalı bir iç-yönlendirme kuralıdır. Gerçek anatomide dendritler çoğunlukla postsinaptik girdi alır, akson terminalleri ise çıkış yapar. Bu nedenle iki kavram kodda ve belgelerde birbirine karıştırılmayacaktır:

1. **Biyolojik sinaptik bağlantı:** Kaynak nöronun akson terminalinden hedef nöronun dendritine giden bağlantı. Pre/post zamanları, salım, reseptör yanıtı ve uygunluk izi bu bağlantıya aittir.
2. **Nöron içi dendritik yönlendirme katkısı:** Bir nöronun dendritik durumunun kendi çıkış sinapslarının yerel aktivasyon potansiyellerini etkilemesi. Bu BrainNew'e özgü hesaplamalı soyutlamadır; gerçek bir dendrit-akson sinapsı olarak adlandırılmaz.

Öğrenme mimarisi her ikisini de destekleyebilir; fakat parametreleri, testleri ve anlamları ayrıdır. Bu ayrım netleşmeden öğrenme güncellemesi yanlış bileşene uygulanabilir. Sprintin ilk zorunlu adımı bu veri/topoloji sözleşmesini kodla birebir eşleştirmektir.

---

## 4. Sprint adımları ve kapı sistemi

Her adımın sonunda testler ve kabul koşulları sağlanır. Bir adım başarısızsa sonraki adım başlatılmaz; önce hata düzeltilir. Kod değişiklikleri küçük, ayrı commit'ler hâlinde tutulur. Sprint boyunca mevcut çalışan davranışlar regresyon testleriyle korunur.

### Adım 1 — Mevcut öğrenme davranışını ölç ve veri/topoloji sözleşmesini sabitle

- Mevcut kodda hangi değişkenin geçici potansiyel, hangisinin kalıcı öğrenilmiş değer olduğunu envanterle.
- Dendrit-sinaps yönlendirme katkısı ile gerçek pre→post bağlantı plastisitesini ayır.
- Her öğrenilmiş parametre için sahibi olan bileşeni tanımla.
- Aynı olayı iki farklı bileşenin iki kez öğrenmediğini doğrula.

Kabul: Her öğrenme değişkeninin anlamı, sahibi, güncelleme olayı, sınırı ve ömrü belgelenmiş olmalı.

### Adım 2 — Öğrenme deneyleri için ölçüm altyapısı

- Deney senaryosu, seed, giriş dizisi, simülasyon süresi ve sonuç ölçütü tanımla.
- Ateşlenme zamanları, sinaps ağırlıkları, dendrit katkıları, uygunluk izleri, modülatör alanları ve yapısal değişimleri dışarı aktar.
- Öğrenme başarısını yalnızca “ağırlık değişti” diye değerlendirme.
- Başlangıç ve bitiş ölçümlerini sakla.

Kabul: Aynı deney aynı seed ile aynı ölçüm dizisini üretmeli; ölçümler öğrenme mekanizmasının iç durumunu açıklayabilmeli.

### Adım 3 — Baseline görevleri kur

En az şu görevler bulunmalı:
- Tek örüntü tanıma/çağırma.
- İki örüntüyü ayırt etme.
- A→B ve B→A sırasını ayırt etme.
- Gürültülü/kısmi girdiden örüntü tamamlama.
- Öğrenme sırasında daha önce görülmemiş test örnekleri.

Eğitim ve test örnekleri ayrılır; test örnekleri öğrenme sırasında ağa verilmez.

Kabul: Öğrenme eklenmeden önce rastgele/başlangıç ağının başarısı ölçülmüş olmalı. Sonraki bütün kazanımlar bu baseline ile kıyaslanmalı.

### Adım 4 — Yerel pre/post etkinlik izleri

- Her gerçek bağlantı presinaptik ve postsinaptik olay zamanlarını/izlerini tutar.
- İzler olay zamanında lazy biçimde güncellenebilir.
- Zaman geriye gidemez; aynı zamanlı olayların sırası deterministiktir.
- İzler kalıcı ağırlık değildir.

Kabul: İzler doğru zaman penceresinde artar, zamanla sönümlenir ve başka bağlantıların izleriyle karışmaz.

### Adım 5 — Hebbian ilişki öğrenmesi

- Önce yalnızca basit ilişki öğrenmesi eklenir.
- Ağırlık sınırları, öğrenme oranı ve normalizasyon test edilir.
- Tekrarlanan ilişki güçlenir; ilgisiz bağlantı etkilenmez.
- Aşırı tekrar ağırlığı sınırsız büyütmez.

Kabul: İlişkili örüntülerin ağırlıkları baseline'a göre değişir; ilgisiz örüntülerde sahte öğrenme sınırlı kalır.

### Adım 6 — Zamansal sıra öğrenmesi (STDP benzeri)

- Pre/post zaman farkı doğru işaretle hesaplanır.
- A→B ile B→A farklı sonuç verir.
- Zaman penceresi dışında etki oluşmaz.
- Aynı olayın iki kez sayılması engellenir.

Kabul: Sıra ters çevrildiğinde öğrenilmiş yanıt da ölçülebilir biçimde değişir.

### Adım 7 — Uygunluk izi ve gecikmiş yerel modülatör

- Yerel pre/post etkinlik uygunluk izini oluşturur.
- Modülatör gelmeden kalıcı güncelleme yapılmaz (bu katmanda).
- Gecikmiş modülatör, yalnızca hâlâ iz taşıyan bağlantıları etkiler.
- İz sönmüşse aynı modülatör kalıcı öğrenme üretmez.
- Pozitif ve negatif modülatör etkileri ayrı test edilir.

Kabul: Aynı modülatör, uygunluk izi taşıyan ve taşımayan bağlantılarda farklı sonuç verir; gecikme arttıkça etki beklenen biçimde azalır.

### Adım 8 — Dendritik yerel katkı öğrenmesini gerçek bağlantı öğrenmesinden ayır

- Mevcut `a_dj` yönlendirme katkısı korunur ve kendi testleri olur.
- Gerçek sinaptik ağırlık/etkinlik gücü ayrı parametre olur.
- Dendritik reseptör profili yalnızca ilgili dendritin yerel yanıtını etkiler.
- Dendritin çıkış sinapsı hazırlama soyutlaması biyolojik sinaps olarak etiketlenmez.

Kabul: Bir mekanizmanın güncellenmesi diğer mekanizmayı istemeden değiştirmez.

### Adım 9 — Homeostaz ve metaplastisite

- Uzun dönem ateşlenme oranı izlenir.
- Homeostatik düzenleme hızlı öğrenmeden daha yavaş çalışır.
- Aşırı etkinlik ve uzun süreli sessizlik senaryoları test edilir.
- Dengeleme, öğrenilmiş ayırt edici örüntüyü yok etmemelidir.

Kabul: Ağ etkinliği kararlı aralıkta tutulurken öğrenilmiş örüntü başarısı korunur.

### Adım 10 — Bağımsız yapısal bakım ve budama

- Her bağlantının bağımsız bakım olayı bulunur.
- Kaynak nöron hiç ateşlenmese bile simülasyon zamanı ilerlediğinde bakım yapılır.
- Kullanım izi aradaki süreyi hesaba katar.
- Kullanılmama tek başına silme nedeni değildir.
- Yerel koruma/budama sinyalleri sonucu etkiler.
- Kopmuş bağlantının eski olayları geçersizleşir.

Kabul: Etkinlikten bağımsız bakım çalışır; yalnızca düşük kullanım + uygun budama koşulları kopma doğurur; korunması gereken bağlantılar rastgele silinmez.

### Adım 11 — Yeni bağlantı oluşumu ve olgunlaşma

- Bağlantısız terminalin yerel aday araması tanımlanır.
- Hedef seçimi yalnızca yerel uygunluk/kimyasal koşullara göre yapılır.
- Yeni bağlantı başlangıçta zayıftır.
- Yeni bağlantı hemen tam olgun kabul edilmez.
- Kopmuş bağlantı ile hiç oluşmamış bağlantı durumları ayırt edilir.

Kabul: Yeni bağlantı yalnızca tanımlı yerel koşullarda oluşur ve olgunlaşması test edilebilir.

### Adım 12 — Öğrenilmiş örüntünün geri çağrılması ve genelleme

- Öğrenme sonrası tam örüntü sunulmadan kısmi/gürültülü ipucu verilir.
- Ağın öğrendiği örüntüyü yeniden oluşturup oluşturmadığı ölçülür.
- Eğitimde görülmeyen ama aynı yapısal ilişkiyi taşıyan örnekler test edilir.
- Ezberleme ile genelleme ayrı raporlanır.

Kabul: Ağ yalnızca eğitim girdisini aynen tekrar etmiyor; tanımlanan test kümesinde anlamlı örüntü tamamlama/ayırt etme başarısı gösteriyor.

### Adım 13 — Uzun süreli öğrenme ve unutma dengesi

- Aynı ağda ardışık farklı görevler öğretilir.
- Yeni öğrenmenin eski örüntüyü ne kadar bozduğu ölçülür.
- Gerektiğinde tekrar/yeniden etkinleştirme ile pekiştirme sınanır.
- Budama ve homeostazın eski öğrenmeyi yok edip etmediği ölçülür.

Kabul: Eski ve yeni görev performansı birlikte raporlanır; unutma gizlenmez veya tek bir toplam puana indirgenmez.

### Adım 14 — Ablasyon ve karşılaştırmalı doğrulama

Her katman ayrı ayrı kapatılarak karşılaştırılır:
- Hebbian yok.
- STDP yok.
- Uygunluk izi/modülatör yok.
- Homeostaz yok.
- Yapısal plastisite yok.

Kabul: Her katmanın hangi görevde ne katkı verdiği ölçülür. İşlevi gösterilemeyen katman gereksiz karmaşıklık olarak yeniden değerlendirilir.

### Adım 15 — Teorik öğrenme sözleşmesini dondur

- Tüm denklemler, parametreler, zaman ölçekleri, sahiplik ve olay akışları tek yerde belgelenir.
- Açık kalan biyolojik/hesaplamalı varsayımlar ayrı işaretlenir.
- Kod ve test isimleri sözleşmeyle eşleştirilir.
- Sonuçlar baseline ve ablation tablolarıyla raporlanır.

Kabul: Başka bir geliştirici, kullanıcıdan sözlü açıklama almadan öğrenme kurallarının ne zaman, nerede ve hangi nedenle çalıştığını anlayabilmeli.

---

## 5. Zorunlu değerlendirme ölçütleri

Her deney aşağıdaki ölçütleri raporlamalıdır:

- Eğitim başarısı.
- Ayrı test kümesi başarısı.
- Örüntü tamamlama başarısı.
- Sıra ayırt etme başarısı.
- Yanlış pozitif/yanlış negatif.
- Öğrenilmiş parametrelerin dağılımı ve doygunluk oranı.
- Ortalama ve dağılım olarak sinaps etkinlikleri.
- Nöronların ateşlenme oranı.
- Ağın sessizleşme veya kontrolsüz etkinleşme oranı.
- Yapısal bağlantı sayısı ve yaşam süresi dağılımı.
- Öğrenme sonrası eski görev performansındaki değişim.
- Seed'ler arası değişkenlik.

Tek bir örnek başarılı sonuç, öğrenme yeteneğini kanıtlamaz. Birden fazla seed ve eğitim/test ayrımı gerekir. Test örnekleri eğitim sırasında ağa gösterilmez.

## 6. Sprintin kapsam dışı bıraktıkları

Bu sprintin hedefi genel zekâ, dil anlama, bilinç veya insan beyninin tam simülasyonu değildir. Ayrıca:
- Gerçek iyon kanalı ve çok bölmeli biyofiziksel dendrit simülasyonu,
- Gen ifadesi/protein sentezinin moleküler ayrıntıları,
- Gerçek anatomik mikroglia hücre hareketleri,
- Beyin ölçeğinde hücre sayısı ve gerçek zamanlı performans,
- İnsan düzeyinde denetimli görev başarısı
bu sprintin kabul koşulu değildir.

Bunlar sonraki araştırma/ölçek aşamalarına bırakılır.

## 7. Bilimsel dayanaklar ve sınırlar

Aşağıdaki kaynaklar farklı öğrenme/plastisite biçimlerinin biyolojik dayanaklarını destekler; BrainNew denklemlerinin birebir biyolojik olduğu anlamına gelmez.

- Magee & Grienberger (2020), *Synaptic Plasticity Forms and Functions*. Hebbian, üç faktörlü, denetimli ve başka plastisite biçimlerinin kapasitelerini ve sınırlılıklarını karşılaştırır. https://doi.org/10.1146/annurev-neuro-090919-022842
- Richards & Lillicrap (2019), *Dendritic solutions to the credit assignment problem*. Dendritik mekanizmaların çok katmanlı devrelerde katkı atamasına olası çözümlerini inceler. https://doi.org/10.1016/j.conb.2018.08.003
- Shouval & Kirkwood (2025), *Eligibility traces as a synaptic substrate for learning*. Gecikmiş ödül/sinyallerin yakın geçmişte etkin olmuş sinapslara nasıl bağlanabileceğini ele alır. https://doi.org/10.1016/j.conb.2025.102978
- Lee & Kirkwood (2019), *Mechanisms of Homeostatic Synaptic Plasticity in vivo*. Sinaptik ölçekleme ve kayan plastisite eşiklerinin ağ kararlılığıyla ilişkisini inceler. https://pubmed.ncbi.nlm.nih.gov/31849610/
- Vogels et al. (2011), *Inhibitory plasticity balances excitation and inhibition in sensory pathways and memory networks*. İnhibitör plastisitenin devre dengesi açısından rolünü modeller. https://www.science.org/doi/10.1126/science.1211095
- Yagishita et al. (2014), *A critical time window for dopamine actions on the structural plasticity of dendritic spines*. Dopamin sinyalinin yakın geçmişte etkin olmuş sinapslarda zamana duyarlı etkisini gösterir. https://www.science.org/doi/10.1126/science.1249098

## 8. Son karar

BrainNew'in öğrenme iddiası, “sinaps ağırlıkları değişiyor” gözlemine dayandırılmayacaktır. Öğrenme; tekrar kullanılabilir örüntü, sıra ayrımı, kısmi ipucundan geri çağırma, test örneklerine genelleme ve eski-yeni bilgi dengesinin ölçülebilir biçimde iyileşmesiyle değerlendirilecektir.

Bu sprintin her adımı ayrı ayrı uygulanır ve doğrulanır. **Teorik tasarım tamamlanmadan bütün mekanizmalar tek seferde koda dökülmez.** Böylece hızlı görünen fakat hangi mekanizmanın ne öğrendiği bilinmeyen bir sistem yerine, kontrollü biçimde sınanabilen bir öğrenme mimarisi elde edilir.
