# BrainNew — Mimari Kararlar ve Genişleme İlkeleri

> **Durum:** Kullanıcı tarafından kabul edilen mimari yönelimleri ve tasarım kısıtlarını kaydeder. Henüz ayrıntıları belirlenmemiş mekanizmalar, sayısal parametreler veya uygulama tercihleri kesinleşmiş sayılmaz. Bu belge kodlama talimatı değil, mimari referanstır.

## 1. Genel tasarım hedefi

BrainNew'de amaç, biyolojik sinir sistemlerinde bulunan her ayrıntıyı birebir simüle etmek değildir. Amaç, öğrenme ve ağ davranışı açısından gerekli işlevleri belirlemek ve bunları mümkün olduğunca düşük hesaplama maliyetiyle gerçekleştirebilen yeterli soyutlamalar kullanmaktır.

Her mekanizma değerlendirilirken şu sıra izlenmelidir:

1. Biyolojik sistemde hangi işlevi yerine getiriyor?
2. BrainNew'in hedeflediği davranışlar için bu işlev gerçekten gerekli mi?
3. İşlev, daha basit bir soyutlamayla korunabilir mi?
4. Mekanizmanın etkileşim ve hesaplama maliyeti nedir?
5. Basitleştirme hangi davranışları kaybettirir ve bu kayıp kabul edilebilir mi?

Biyolojik varlık tek başına ayrıntılı simülasyon gerekçesi değildir. Moleküler veya hücresel ayrıntılar, ancak hedeflenen işlev için gerekli oldukları gösterildiğinde eklenmelidir.

## 2. Sinir ağı çekirdeği ve sorumluluk sınırları

- Sinir ağı çekirdeği görselleştirme aracından bağımsız çalışabilmelidir.
- Beyin yalnızca simülasyon zamanını, olay akışını ve bileşenler arası koordinasyonu yöneten orkestratördür.
- Öğrenme ve sinaptik değişiklik kararları ilgili nöronlara ve yerel bileşenlere ait kalır; orkestratör bunları merkezi olarak belirlemez.
- Dış deney araçları sinaptik ağırlıkları veya öğrenme kararlarını doğrudan değiştiremez. Yalnızca tanımlı uyarım/çevre arayüzleri üzerinden etki eder.
- Gözlem ve telemetri katmanı sinir ağının iç durumunu değiştiremez.

## 3. Tekrarlayan ve döngüsel bağlantılar

Ağ topolojisi döngüsel bağlantıları engellememelidir. Aşağıdaki bağlantı türleri desteklenmelidir:

- Tekrarlayan yollar: A → B → C → A.
- Öz bağlantılar: A → A.
- Karşılıklı bağlantılar: A → B → A.
- Birden fazla nöron arasında geri besleme döngüleri ve kendini sürdürebilen etkinlik örüntüleri.

Bu bağlantılar mimari olarak yasaklanmayacaktır. Ancak döngülerin varlığı, aynı simülasyon anında sınırsız olay işlenmesine izin verildiği anlamına gelmez. İletim gecikmeleri, olay kuyruğu ve nöronların zamanlama/refrakter kuralları kararlı bir yürütme sağlamalı; sıfır zamanlı sonsuz olay zincirleri engellenmelidir.

## 4. Reseptör ve motor organ arayüzleri

Sinir ağı dış dünyadan girdi alabilmeli ve çıktı üretebilmelidir. Bu etkileşim doğrudan ağın iç durumlarına rastgele değer yazmak yerine ayrı organ arayüzleri üzerinden yapılmalıdır.

### Reseptör organları — girdi

- Deneyci/operatör tarafından verilen girdileri alır.
- Dış girdiyi sinir ağına aktarılabilecek sinyallere dönüştürür.
- İlk aşamada elle verilen basit sayısal girdiler desteklenebilir.
- Arayüz belirli bir veri türüne veya tek bir duyuya sabitlenmemeli; ileride farklı girdi kanalları eklenebilmelidir.

### Motor organları — çıktı

- Sinir ağının ürettiği motor/çıkış sinyallerini alır.
- Bu sinyalleri dışarıya sunulabilir ve kaydedilebilir çıktılara dönüştürür.
- Öğretim ve deneylerde ağın performansı motor organ çıktısı üzerinden izlenir.

### Öğretim döngüsü

1. Operatör girdiyi reseptör organ üzerinden verir.
2. Reseptör organ girdiyi sinir ağına aktarır.
3. Ağ kendi yerel mekanizmalarıyla etkinlik üretir ve işler.
4. Motor organ ağın çıktısını dışarı aktarır.
5. Çıktı gözlemlenir ve değerlendirilir.
6. Gerekirse operatör yeni bir girdi veya çevresel müdahale uygular.

Motor organın çıktısı gözlem/değerlendirme noktasıdır; kendisi öğrenme algoritması veya sinaptik düzeltme mekanizması değildir. Öğrenme kararları ağın yerel mekanizmalarında kalır. Geri bildirim türlerinin ve öğretim protokollerinin ayrıntıları ayrıca tasarlanacaktır.

## 5. Gözlem, telemetri ve görselleştirme

Çalışan bir sinir ağının canlı olarak izlenebilmesi BrainNew'in temel hedeflerinden biridir; sonradan eklenen tali bir özellik olarak görülmemelidir.

Bu nedenle çekirdek ile görselleştirme arasında bağımsız bir gözlem/telemetri sınırı bulunmalıdır.

### Telemetri katmanının sorumlulukları

İhtiyaca göre aşağıdaki bilgileri dışarı aktarabilmelidir:

- Nöron ateşleme olayları ve zamanları.
- Nöron, dendrit ve sinapsların seçilmiş durum değişkenleri.
- Sinaptik etkinlik ve bağlantı değişimleri.
- Kimyasal alan/sinyal yoğunlukları.
- Ağ topolojisi ve bağlantıların yapısal durumu.
- Motor organlardan çıkan ağ çıktıları.

Gözlem verisi mümkün olduğunca olay/değişim odaklı aktarılmalı; görselleştirme için her simülasyon adımında bütün ağın gereksiz yere kopyalanması zorunlu hale getirilmemelidir. Gözlem kapalıyken çekirdek çalışmaya devam edebilmelidir.

### Görselleştirme aracı

- Pygame ilk 2D gözlem aracı için uygun bir adaydır; ancak kesin teknoloji seçimi değildir.
- Görselleştirme arayüzü değiştirilebilir olmalıdır. Daha sonra GPU hızlandırmalı veya başka bir görselleştirme çözümüne geçmek için sinir ağı çekirdeği yeniden yazılmamalıdır.
- İlk hedef, nöronları ve bağlantıları; etkinlikleri ve zaman içindeki değişimleri canlı izleyebilmektir.
- İleride topoloji, ateşleme, sinaptik durum, kimyasal alan ve motor çıktılar için farklı görünüm/analiz katmanları eklenebilir.
- Görselleştirme salt okunur olmalıdır. Deneysel müdahaleler ayrı ve açıkça tanımlanmış kontrol arayüzlerinden yapılmalıdır.

## 6. Deney ortamıyla ilişki

Deney ortamı, sinir ağı çekirdeğinin parçası değil; ona tanımlı arayüzlerle bağlanan ayrı bir katman olmalıdır.

Bu katman ileride şunları sağlayabilir:

- Reseptör organlar üzerinden elle veya protokolle girdi verme.
- Elektriksel uyarım uygulama.
- Kimyasal alana kontrollü müdahale etme.
- Motor organ çıktılarını ve ağ yanıtlarını kaydetme.
- Ölçülen yanıta göre yeni müdahale seçme (kapalı döngü deney).

Deney ortamının kapsamı ve araçları henüz kesinleştirilmemiştir. Mevcut deneysel müdahale fikirleri `_in_proggres_ideas.md` dosyasında taslak olarak tutulur.

## 7. Henüz karara bağlanmayan konular

Aşağıdakiler yönelim olarak belirlenmiş olsa da ayrıntılı tasarım gerektirir:

- Biyolojik mekanizmaların hangilerinin gerekli, hangilerinin birleştirilebilir veya çıkarılabilir olduğu.
- Her mekanizma için en düşük maliyetli yeterli soyutlama.
- Reseptör ve motor organların veri/sinyal sözleşmeleri ve birden fazla kanalın nasıl temsil edileceği.
- Geri bildirim ile dışarıdan verilen öğretim/deney müdahalelerinin kesin ayrımı ve protokolleri.
- Telemetri olay şeması, örnekleme sıklığı, performans bütçesi ve kayıt biçimi.
- Pygame veya alternatif görselleştirme teknolojisinin seçimi.
- Döngüsel ağlarda gecikme, refrakter dönem ve olay kuyruğu kurallarının sayısal ayrıntıları.

Bu kararlar netleşmeden sayısal parametreler uydurulmamalı veya uygulama ayrıntıları kesinleşmiş gibi kodlanmamalıdır.
