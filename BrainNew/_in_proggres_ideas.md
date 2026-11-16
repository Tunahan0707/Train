# BrainNew — İleride İncelenecek Fikirler

> **Durum:** Taslak fikir havuzu. Bu belgedeki başlıklar henüz mimari kararı değildir; mevcut mekanizmaları değiştirmez ve kodlama talimatı oluşturmaz. Kabul edilmiş mimari yönelimler için [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) dosyasına bakın. Bu fikirler ileride biyolojik literatür ve deney sonuçları ışığında tartışılıp güncellenecektir.

## 1. Az kullanılan sinapsların korunması ve desteklenmesi

### Problem

Mevcut yaklaşımda az kullanılan bir sinaps, kullanım geçmişi nedeniyle zamanla dezavantajlı duruma düşebilir. Ancak düşük kullanım tek başına bağlantının işlevsiz veya gereksiz olduğunu göstermez. Seyrek kullanılan, henüz uygun örüntüyle karşılaşmamış veya başka bağlantılarla birlikte anlam kazanan sinapslar da bulunabilir.

### İncelenecek biyolojik mekanizmalar

- **Nörotrofik destek:** BDNF gibi nörotrofik faktörlerin nöron ve sinapsların yaşaması, gelişmesi ve plastisitesi üzerindeki etkileri. Modelde kimyasal destek sinyallerinin sinaptik bütünlük/olgunluk üzerindeki olası rolü incelenebilir.
- **Synaptic Tagging and Capture:** Etkinlik sonrasında sinapsta oluşan geçici etiketin, daha genel hücresel plastisite süreçlerinde üretilen ürünleri yakalayarak değişimin kalıcılığına katkıda bulunması. Bu mekanizma hiç etkinleşmemiş sinapsların otomatik korunması şeklinde yorumlanmamalı.
- **Heterosinaptik plastisite:** Bir sinapstaki etkinliğin aynı nöron üzerindeki başka sinapsları da güçlendirebilmesi veya zayıflatabilmesi. Mevcut sinaps-sinaps etkileşimleriyle ilişkisi araştırılmalı.
- **Mikroglia aracılı bakım:** Mikroglia benzeri yapıların yalnızca budama değil, bağlantıların korunması ve yapısal durumlarının düzenlenmesindeki olası rolleri.

### Tasarımda korunması gereken ayrımlar

- Kullanım geçmişi ile yapısal yaşama/bütünlük durumu ayrı kavramlar olmalı.
- Az kullanım otomatik olarak işlevsel zayıflama veya fiziksel eliminasyon anlamına gelmemeli.
- Koruma, bakım, işlevsel zayıflama ve fiziksel eliminasyon birbirinden ayrı süreçler olarak incelenmeli.
- Kimyasal destek sınırsız veya bütün sinapslara eşit dağıtılan bir ödül mekanizmasına dönüşmemeli; yerel koşullar ve rekabet dikkate alınmalı.

## 2. Feedback ve deneysel müdahale sisteminin genişletilmesi

Mevcut pozitif/negatif öğrenme feedback'i, biyolojik deneylerdeki bütün müdahale ve geri bildirim biçimlerini kapsamıyor. Bu nedenle aşağıdaki kavramlar ayrı tutulmalı:

1. **Elektriksel müdahale:** Seçilen nörona, sinapsa, dendrit bölgesine veya uzamsal konuma kontrollü elektriksel uyarım uygulama.
2. **Kimyasal müdahale:** Kimyasal alana belirli sinyal türü/miktarı bırakma, yerel yoğunluğu değiştirme veya belirli sinyalin etkisini engelleme.
3. **Gözlem ve ölçüm:** Ateşleme, membran potansiyeli, sinaptik etkinlik, kimyasal yoğunluk ve yapısal değişimleri kaydetme.
4. **Koşullu/kapalı döngü müdahale:** Ölçülen nöral cevaba göre sonraki elektriksel veya kimyasal müdahaleyi değiştirme.

**Mimari sınır:** Deney düzeneği dışarıdan koşulları değiştiren ve ölçüm yapan araç olmalı. Müdahale doğrudan sinaptik ağırlıkları veya öğrenme kararlarını yazmamalı; yerel öğrenme kararları nöronlara ve ilgili yerel bileşenlere ait kalmalı. Beyin yine orkestratör olmalı.

## 3. Kontrollü deney ortamları

Deney altyapısının sinir sistemi modelinden ayrı bir katman olarak tasarlanması değerlendirilecek. Amaç tek bir nörondan bütün ağa kadar farklı ölçeklerde kontrollü deney yapabilmek.

### Deney ölçekleri

- **İzole nöron:** Elektriksel uyarımın şiddeti, süresi, sıklığı ve zamanlamasını değiştirerek ateşleme eşiği, membran potansiyeli ve cevap davranışını inceleme.
- **İzole bağlantı / nöron çifti:** Kaynak ve hedef nöronun zamanlamasını kontrol ederek sinaptik iletimi ve plastisiteyi inceleme.
- **Kimyasal ortam deneyi:** Kimyasal sinyali tür, miktar, konum ve zaman bakımından kontrollü uygulama; yayılımı ve etkileri gözlemleme.
- **Ağ düzeyi deney:** Çoklu elektrot dizisi (MEA) benzeri soyut bir arayüzle ağın belirli bölgelerini uyarma ve eşzamanlı etkinlik kaydı alma.
- **Manuel/operatör kontrollü eğitim:** Araştırmacının uyarım uygulayıp cevabı gözlemlemesi, sonraki müdahaleyi buna göre değiştirmesi. Bu, nörona doğrudan “öğren” komutu vermek değil, deney koşullarını değiştirmek olmalı.

### Deney düzeneğinde düşünülebilecek araçlar

| Araç | İşlev |
|---|---|
| Elektriksel uyarıcı | Seçilen hedefe kontrollü elektriksel sinyal gönderme |
| Kimyasal uygulayıcı | Kimyasal alana kontrollü sinyal bırakma veya alanı değiştirme |
| Kayıt/ölçüm aracı | Nöral ve kimyasal etkinliği kaydetme |
| Gözlem aracı | Ağ topolojisini, etkinliği ve değişimleri inceleme |
| Deney kontrolcüsü | Önceden tanımlanan veya cevaba bağlı müdahale protokollerini yürütme |
| Snapshot/karşılaştırma | Deney öncesi ve sonrası durumları kaydetme; aynı başlangıçtan kontrol ve deney kopyaları üretme |

Deneyciye yalnızca ölçülebilir çıktıları gösteren bir mod ile araştırma amacıyla iç durumları gösteren tanılama modu ayrı düşünülebilir. Böylece müdahale sırasında gizli iç durumlara erişimin sonucu etkilemediği deneyler de yapılabilir.

## 4. Sonradan tasarlanabilecek deney hipotezleri

- Kimyasal destek, az kullanılan fakat yapısal olarak sağlıklı sinapsların korunmasına katkıda bulunabilir mi?
- Hiç veya çok az etkinleşmeyen bir sinaps, etkinlikten bağımsız bakım koşullarında ne kadar süre bütünlüğünü korur?
- Bir sinapsın etkinliği aynı nöron üzerindeki diğer sinapsları nasıl etkiler?
- Kimyasal ortamın değiştirilmesi sinaptik öğrenmeyi ve yapısal bakımı nasıl etkiler?
- Elektriksel uyarımın sıklığı, şiddeti ve zamanlaması nöron/sinaps davranışını nasıl değiştirir?
- Nöral cevaba göre uyarlanan kapalı döngü müdahalesi, sabit uyarım protokolünden farklı sonuç verir mi?
- Dış müdahale kaldırıldığında edinilmiş değişim ne ölçüde korunur?
- Mikroglia benzeri bakım etkinliği azaltıldığında bağlantıların bütünlüğü ve ömrü nasıl değişir?

Deneylerde mümkün olduğunca tek bir bağımsız değişken değiştirilmesi; başlangıç durumunun, rastgelelik durumunun, müdahale protokolünün ve ölçümlerin kaydedilmesi gerekir.

## 5. Literatür inceleme başlıkları

İleride birincil kaynakları ve deney koşullarını yeniden doğrulayarak incelenecek araştırma alanları:

- Nörotrofik faktörler ve sinaptik bakım (özellikle BDNF).
- Synaptic Tagging and Capture.
- Heterosinaptik plastisite.
- Mikroglia-sinaps etkileşimi ve sinaptik bakım/budanma.
- Kültürlenmiş nöron ağlarında çoklu elektrot dizileri (MEA).
- Elektriksel uyarım ve kapalı döngü nöral deneyler.
- Nöron kültürleri ile yapay ajan/robot arasında kapalı döngü etkileşim.

Bu başlıklar, tek başına BrainNew'de aynı mekanizmaların uygulanması gerektiğini kanıtlamaz. Biyolojik bulgu, kullanılan deney sistemi ve BrainNew'e yapılabilecek soyutlama ayrı ayrı değerlendirilmelidir.

## 6. İleride ele alma sırası için öneri

1. Mevcut sinaps yaşlanması, kullanım geçmişi, bütünlük ve mikroglia davranışını inceleyip tam olarak nerede sorun oluştuğunu belirlemek.
2. Kullanım dışı sinaps desteği için biyolojik mekanizmaları karşılaştırmak.
3. Feedback kavramlarını müdahale, ölçüm ve öğrenme kararı olarak net biçimde ayırmak.
4. İzole nöron ve sinaps deneylerinin gereksinimlerini belirlemek.
5. Elektriksel/kimyasal müdahale ve kapalı döngü protokollerini tasarlamak.
6. Deney kayıtları, snapshot ve tekrarlanabilirlik altyapısıyla entegrasyonu planlamak.

**Şimdilik uygulanmayacak:** Bu belge fikirleri saklar. Mevcut mimariyi değiştirmez, yeni parametre veya mekanizma kararı vermez ve kodlama başlatmaz.
