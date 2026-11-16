# BrainNew — Yerel Yapısal Plastisite Tasarımı

## Amaç

Kopmuş bağlantıların geri döndürülmesi ile yeni bağlantı oluşturulmasını birbirinden ayırmak. Yeni bağlantı, eski sinapsın otomatik diriltilmesi değildir; yeni kimlikli, başlangıçta zayıf ve olgunlaşmaya ihtiyaç duyan ayrı bir yapıdır.

## Değişmez mimari kurallar

- Beyin yalnızca uzamsal komşuluk sorgusunu ve olay/zaman koordinasyonunu sağlayabilir. Hangi nöronun hangi dendrite bağlanacağına karar veremez.
- Bağlantı kurma kararı yerel nöron/dendrit mekanizmalarında verilir.
- Tam ağ üzerinde her adımda tarama veya tüm nöron çiftlerini karşılaştırma yapılmaz.
- Uzamsal model 2B kalır; adaylık için karesel Öklid uzaklığı kullanılır.
- Yeni bağlantı karşılıklı kayıtla oluşturulur: kaynak çıkış listesi, hedef giriş listesi, hedef dendrit ve kaynak dendritin terminal-katkı haritası.
- Yeni bağlantı ilk anda zayıf olmalı; etkinlik, yerel büyüme/stabilizasyon kimyası ve kullanım ile kademeli olgunlaşmalı.
- Fiziksel kopma ile düşük sinaptik ağırlık ayrı kalır. Kopmuş bağlantı yeniden etkinleştirilmez.

## Önerilen yerel oluşum döngüsü

1. **Aday keşfi:** Uzamsal indeks, yerel büyüme sürecine yalnızca belirli yarıçaptaki nöron/dendrit adaylarını sunar. İndeks karar vermez.
2. **Yerel uygunluk:** Kaynak nöronun büyüme sinyali ve hedef dendritin kimyasal reseptör yanıtı değerlendirilir. Uygunluk yoksa bağlantı kurulmaz.
3. **Tekilleştirme:** Aynı kaynak-hedef-dendrit üçlüsü için ikinci paralel bağlantı, açıkça izin verilmedikçe engellenir.
4. **Oluşum:** Yeni `Baglanti` benzersiz kimlikle, düşük `sinaptik_agirlik`, düşük başlangıç yapısal bütünlük veya ayrı olgunlaşma durumu ile kurulur.
5. **Kayıt:** Kaynak nöron, hedef nöron ve ilgili dendritlerin bağlantı kayıtları tutarlı biçimde güncellenir.
6. **Olgunlaşma:** Kullanım izi ve yerel stabilizasyon/büyüme sinyali bağlantıyı korur. Kullanılmayan ve budama sinyali alan yeni bağlantı kopabilir.
7. **Gözlem:** Oluşum, olgunlaşma, başarısız aday ve kopma olayları pasif deney kaydına yazılır.

## Uygulama — uzamsal aday indeksi ve yerel yeni bağlantı oluşumu

`UzamsalIndeks.py` içinde sabit hücreli 2B uzamsal indeks eklendi. İndeks:
- Nöronları kimlikleriyle hücrelere kaydeder ve yinelenen kimliği reddeder.
- Yalnızca arama yarıçapıyla kesişebilecek hücreleri tarar; son adayları karesel Öklid uzaklığıyla filtreler.
- Adayları uzaklık ve kimlik anahtarına göre deterministik sıralar.
- Kayıt silme ve hücreler arası konum güncellemesini destekler.
- Bağlantı kurmaz ve yerel uygunluk kararı vermez.

Bağlantı indeksi mikroglia için sinaps terminallerini, ayrı `noron_indeksi` ise büyüme sürecindeki yakın nöronları tutar. `Beyin.yapisal_buyume_degerlendir` yalnızca yakın adayları sorgular ve listeyi kaynak nörona verir. Kaynak nöron, kendi konumundaki `buyume` kimyasalını ve hedef dendritin `buyume` reseptör yanıtını değerlendirerek en uygun hedefi yerel olarak seçer. Beyin bağlantı seçmez.

## İlk sürümün sınırları ve henüz karara bağlanmamış ayrıntılar

- İlk sürümde büyüme denemesi açıkça `Beyin.yapisal_buyume_degerlendir(noron_id, arama_yaricapi)` çağrısıyla başlatılır; otomatik deneme sıklığı henüz yoktur.
- Kaynak büyüme eşiği, hedef reseptör uygunluk eşiği, başlangıç ağırlığı ve yapısal bütünlük kalibrasyon parametreleridir; biyolojik sabit değildir.
- İlk sürüm hedef adaylarını nöron konumuyla bulur, ardından dendrit konumunu ayrıca yarıçapla denetler.
- Yeni bağlantının kaynak nöronundaki her dendrit katkısı, nöron kimliğinden türetilen tekrarlanabilir rastgele akışla [-0.1, 0.1] aralığında başlatılır.
- Yeni bağlantı oluşumunun eğitim/test ayrımını ihlal etmeden değerlendirilmesi ve ölçek profili ayrıca yapılmalıdır.

## Zorunlu testler

- Yarıçap dışındaki aday hiçbir zaman bağlantı alamaz.
- Yerel büyüme/uygunluk sinyali yokken bağlantı oluşmaz.
- Oluşan bağlantı kaynak, hedef ve dendrit kayıtlarında aynı nesne kimliğiyle görünür.
- Aynı üçlü için yinelenen bağlantı oluşmaz.
- Yeni bağlantı zayıf başlar; ilk anda güçlü ve olgun bağlantı gibi davranmaz.
- Bağlantı kopunca tüm ilgili listelerden ve dendrit haritalarından temizlenir.
- Beyin'in bağlantı seçimi veya öğrenme parametresi güncellemesi yaptığı bir kod yolu bulunmaz.
- Aday keşfi tüm ağ üzerinde her olayda tarama yapmaz.
- Aynı başlangıç koşulları aynı bağlantı oluşum sırasını üretir.

## Uygulama sırası

1. Salt uzamsal komşuluk sorgusu ve karmaşıklık testi. (İndeksin ilk uygulaması eklendi; kullanıcı test doğrulaması ve ölçek testi bekleniyor.)
2. Yerel aday uygunluğu ve deterministik seçim.
3. Güvenli bağlantı kurma/tekilleştirme API'si.
4. Zayıf başlangıç ve olgunlaşma.
5. Budama ile yaşam döngüsü entegrasyonu.
6. Deney sürücüsünde yapısal plastisite ölçümleri.

Yeni bağlantı oluşturmanın ilk kontrollü sürümü uygulanmıştır; otomatik büyüme zamanlaması, olgunlaşma dinamiği ve görev düzeyinde katkısı henüz uygulanmamıştır.
