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

## Henüz karara bağlanmamış teknik ayrıntılar

- Uzamsal indeksin sahibi: Beyin içinde salt sorgu hizmeti mi, yoksa ayrı bir uzamsal ortam bileşeni mi?
- Kaynak terminali ile hedef dendritin büyüme yönünü belirleyen yerel sinyalin matematiksel biçimi.
- Yeni bağlantının başlangıç ağırlığı, yapısal bütünlüğü ve olgunlaşma zaman sabiti.
- Aday deneme sıklığının olay yoğunluğundan bağımsız ve hesaplama açısından sınırlı tutulması.
- Yeni bağlantıların eğitim/test ayrımını ihlal etmeden değerlendirilmesi.

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

1. Salt uzamsal komşuluk sorgusu ve karmaşıklık testi.
2. Yerel aday uygunluğu ve deterministik seçim.
3. Güvenli bağlantı kurma/tekilleştirme API'si.
4. Zayıf başlangıç ve olgunlaşma.
5. Budama ile yaşam döngüsü entegrasyonu.
6. Deney sürücüsünde yapısal plastisite ölçümleri.

Bu belge tasarım sözleşmesidir; henüz üretim koduna yeni bağlantı oluşturma davranışı eklemez.
