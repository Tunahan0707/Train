# BrainNew — Gelişim ve Beyin Durumu Saklama Planı

Durum: Tasarım kararı kabul edildi; uygulama planına alındı. Bu belge kodun mevcut durumda bu özellikleri sunduğu anlamına gelmez.

## 1. Gelişim mekanizması

### Amaç
Önceden belirlenmiş bir bağlantı haritasını aktarmadan, basit ve yerel kurallarla bireysel ağın bağlantılarını oluşturup olgunlaştırmak. Beyin yalnızca zamanı, olayları ve uzamsal aday sorgusunu koordine eder; bağlantı oluşumu, korunması ve değişimi yerel bileşenlerin kararıdır.

### İki başlangıç modu

- Mevcut rastgele seyrek ağ (AgKurucu): kontrol/baseline olarak korunur. Aynı seed ile tekrarlanabilir başlangıç topolojisi sağlar.
- Gelişimden oluşan ağ (yeni mod): sabit 2B nöron yerleşimi ve mevcut dendrit/terminal altyapısıyla başlar; başlangıçta işlevsel pre→post bağlantıları yoktur. Bağlantılar gelişim sürecinde yerel büyüme kurallarıyla oluşur.

Bu iki mod birbirinin yerine sessizce geçirilmez. Aynı görevlerde karşılaştırılabilmeleri için ayrı tutulur. Gelişimden oluşan mod, mevcut AgKurucu davranışını silmez.

### Gelişim döngüsü

1. Başlangıç organizasyonu: Nöron konumları ve yerel dendrit/terminal yapıları oluşturulur. İlk sürümde nöron göçü ve yeni nöron üretimi simüle edilmez.
2. Yerel bağlantı arama: Uzamsal indeks yalnızca yakın adayları verir. Kaynak nöron; mesafe, yerel çekici/itici kimyasal ipuçları, hedef dendrit uygunluğu ve sınırlı stokastiklik üzerinden kendi bağlantı kararını verir.
3. Zayıf bağlantı oluşumu: Yeni sinaps düşük ağırlık ve düşük işlevsel olgunlukla başlar. Kaynak, hedef ve dendrit kayıtları tutarlı biçimde güncellenir.
4. Kendiliğinden etkinlik: Ağda seyrek ve düşük oranlı spontan etkinlik bulunabilir. Her nöronun sürekli rastgele ateşlemesi kullanılmaz.
5. Yerel rekabet ve olgunlaşma: Kullanım, zamansal birlikte etkinlik, yerel kimyasal sinyaller ve mevcut olgunluk bağlantıların korunma/olgunlaşma eğilimini etkiler. Yalnızca sessizlik otomatik budama gerekçesi yapılmaz; rekabet bağlamı aranır.
6. Bakım ve budama: Bağımsız mikroglia-benzeri ajanlar kendi yerel alanlarındaki bağlantıları değerlendirir. Kullanım geçmişi, birlikte etkinlik, yapısal bütünlük/olgunluk ve kimyasal ipuçları birlikte ele alınır. İşlevsel zayıflama ile fiziksel kopma ayrı tutulur.

Aşamalar katı ve küresel bir takvimle değil, yerel olgunluk/etkinlik durumlarıyla örtüşerek ilerler. Erken dönemde bağlantı arama daha sık; ilerleyen dönemde oluşum daha seyrek olabilir, bakım ve öğrenme devam eder.

### Kimyasal işaretler

- Mevcut 2B kimyasal alan yeniden kullanılır; gereksiz ikinci bir difüzyon altyapısı eklenmez.
- Yön bulma/bağlantı rehberliği işaretleri, hızlı sinaptik transmitterlerle kavramsal olarak aynı şey sayılmaz. Aynı hesaplamalı alan içinde ayrı işlevsel türler olarak temsil edilebilir.
- İlk sürümde ayrıntılı moleküler yolaklar veya çok sayıda hücre tipi eklenmez.

### Korunan ilkeler ve kapsam dışı

- Beyin orkestratördür; yerel büyüme, öğrenme ve budama kararlarını vermez.
- 2B uzamsal model, seyrek yerel arama ve sınırlı parametreler korunur.
- İlk sürümde nörogenez, hücre göçü, ayrıntılı akson büyüme konisi fiziği, iyon kanalı simülasyonu, moleküler yolaklar ve ayrı astroglia simülasyonu yoktur.
- Mevcut işaretli sinaptik etki soyutlaması korunur; bu aşamada yeni bir uyarıcı/baskılayıcı hücre tipi taksonomisi dayatılmaz.
- Evrimsel arama, tek bir beynin gelişiminden ayrıdır. Daha sonra farklı seed ve gelişim parametrelerini dış deney döngüsünde karşılaştırabilir.

### Deneysel kontrol

Gelişimden oluşan ağ, mevcut rastgele seyrek ağla aynı görev ve ölçüm protokolünde karşılaştırılır. Çoklu seed, öğrenme/genelleme, kararlılık, bağlantı sayısı ve hesaplama maliyeti ölçülür. Büyüme, spontan etkinlik, rekabet ve mikroglia mekanizmaları ayrı ayrı ablasyon testlerine tabi tutulur. Başarı varsayılmaz; ölçülür.

## 2. Beyin kaydetme/yükleme ve deney dallandırma

### Amaç
Beğenilen bir beynin tam durumunu dondurmak, daha sonra aynı noktadan devam etmek ve aynı başlangıç durumundan bağımsız deney kopyaları üretmek.

### Planlanan arayüz

- Beyin.kaydet(dosya_yolu): sürümlendirilmiş tam durum görüntüsü yazar.
- Beyin.yukle(dosya_yolu): kaydedilen durumu yeni bir Beyin örneği olarak geri kurar.
- Beyin.kopya_olustur() veya save/load tabanlı eşdeğer: aynı durumdan bağımsız deney kopyası oluşturur.

İsimler uygulama aşamasında kesinleştirilebilir; davranış sözleşmesi aşağıdaki gibidir.

### Saklanması gereken durum

- Nöron kimlikleri, konumları, tüm öğrenilmiş ve geçici nöral durumları.
- Dendritler, reseptör duyarlılıkları, dendrit-terminal katkıları ve değerlendirme izleri.
- Bağlantı topolojisi, kimlikler, hedef dendritler, ağırlıklar, eşikler, potansiyeller, pre/post/uygunluk izleri, yapısal bütünlük ve olgunluk.
- Sinaps-sinaps ve nöron-nöron ilişkileri.
- Mikroglia ajanları, konumları, tarama/bakım durumları.
- Kimyasal alan kaynakları ve bütün alan parametreleri.
- Simülasyon zamanı, bekleyen olay kuyruğu, olay sayaçları, entegrasyon planları ve otomatik bakım durumu.
- Tekrarlanabilir devam için kullanılan rastgele sayı üreteçlerinin durumları.
- Ağ kurulum/gelişim parametreleri ve deney metadata'sı.

Sadece ağırlıkları/topolojiyi kaydetmek tam snapshot değildir. Bekleyen olaylar, geçici izler, kimyasal kaynaklar ve rastgele sayı üreteci durumu da korunmalıdır.

### Biçim ve güvenlik

- Sürüm numarası taşıyan JSON şeması; dosya boyutu büyürse isteğe bağlı gzip.
- Python pickle kullanılmaz.
- Nesne referansları doğrudan bellekteki pointer'lar olarak değil, kararlı kimlikler üzerinden serileştirilir ve yüklemede yeniden bağlanır.
- Yükleme, eksik kimlikleri ve geçersiz referansları doğrular; bozuk veya desteklenmeyen şema sürümünü açık hata ile reddeder.
- Kaydetme atomik yazılır; yarım kalmış dosya geçerli snapshot gibi görünmez.

### Kabul testleri

1. Kaydet/yükle sonrası ağ topolojisi ve öğrenilmiş parametreler eşleşir.
2. Bekleyen olayları bulunan ağ yüklenince aynı olay sırası ve aynı sonraki durum oluşur.
3. Kimyasal kaynaklar, geçici izler, mikroglia bakım planları ve simülasyon zamanı korunur.
4. Aynı snapshot'tan yüklenen iki kopya birbirinden bağımsız değişebilir.
5. Aynı seed ve snapshot'tan devam eden deneyler deterministik sonuç üretir.
6. Geçersiz/gelecekteki şema sürümü güvenli biçimde reddedilir.

## 3. Pasif aktivasyon izi

ActivationTrace olay kuyruğu olaylarını, nöron ateşlenmelerini ve gerçekten aktive edilen sinapsları kaydeden tanılama aracıdır. Nedensel girdi sinapslarından geriye iz sürmeye yardımcı olur. Öğrenme izi (Baglanti.uygunluk_izi) ile aynı şey değildir ve hiçbir öğrenme kararına müdahale etmez.

## 4. İleride değerlendirilecek fikirler — aktif sprint değil

Aşağıdakiler kabul edilmiş mimari genişleme yönleridir; şu anki uygulama kapsamına alınmamıştır.

### 4.1 Duyusal-motor kapalı döngü
Ayrı bir beden/çevre simülasyonu; duyusal ölçümler; motor komutlar; hareketin gerçek sonucundan geri besleme. Motor öğrenme, yalnızca başarı/başarısızlık ödülüyle değil, gerçekleşen hareket ve beklenen/ölçülen beden durumu farkıyla bilgilendirilebilir. Bu katman mevcut sinaptik öğrenme mekanizmasının yerine geçmez.

### 4.2 Fizyoloji ve enerji
Enerji bütçesi, metabolizma ve iç durum düzenlemesi. Sinir sistemi dışındaki beden/fizyoloji bileşenleri olarak tasarlanır; Brain sınıfına gömülmez.

### 4.3 Otonom davranış
Kaynak arama, çevreye uyum ve kendi iç dengesini koruma gibi davranışların duyusal-motor ve fizyolojik katmanlar üzerinde ortaya çıkıp çıkmadığını incelemek. Hazır davranış senaryoları olarak sinir ağına kodlanmaz.

Bu üç fikir, sinir sisteminin öğrenme ve hafıza davranışı yeterince ölçülmeden uygulanmayacaktır.
