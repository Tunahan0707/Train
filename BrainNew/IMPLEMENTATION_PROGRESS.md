# BrainNew — Uygulama ilerlemesi

Hedef dal: `fix/brainnew-architecture-audit`

## Uygulananlar

- [x] Aynı simülasyon ağı üzerinde episode'lar arası kalıcı parametreleri koruyan `EgitimSurucusu` temeli eklendi.
- [x] `Beyin.episode_baslat()` geçici nöral durumları temizler; öğrenilmiş sinaptik ağırlıkları, dendrit-terminal katkılarını ve bağlantı topolojisini korur.
- [x] `ReseptorOrgan` ve `MotorOrgan` için en küçük kullanılabilir girdi/çıktı arayüzleri eklendi.
- [x] Nöronun yerel feedback metodu, pozitif feedback'te etkin sinaps eşiğini düşürüp etkin olmayanı yükseltir; negatif feedback bunu tersine çevirir.
- [x] İlk dallanan geriye feedback prototipi eklendi: son ateşlenmenin nedensel girdileri üzerinden ters yönde, yerel presinaptik iz ve dal sönümüyle ilerler; Beyin yalnızca olayları zamanlar.
- [x] Aynı nöronun çıkış sinapsları arasında seyrek, yönlü sinaps-sinaps ilişkileri eklendi; birlikte etkinleşme, tek taraflı etkinleşme, geçici potansiyel etkisi ve tembel sönüm testleri yazıldı.
- [x] Yakın nöronlar arasında zaman pencereli yerel birlikte etkinlik izi ve yönlü ilişki eklendi; aynı zaman damgasında iki yön öğrenilir, sıralı etkinlikte önceki→sonraki yön öğrenilir. İlişki bağlantı büyüme uygunluğunu sınırlı ölçüde etkiler.
- [x] Kopmuş bağlantıdan daha önce kuyruğa alınmış sinaptik olayın hedefe ulaşması engellendi.
- [x] Bağlantı olgunluğu fiziksel bütünlükten ayrıldı; mikroglia kullanımla/stabilizasyonla olgunlaştırır, budama sinyaliyle işlevsel olgunluğu düşürür. Yeni bağlantılar düşük olgunlukla başlar.
- [x] Refrakter dönemde gelen girdi dendritte tamponlanır; faz döngüsü tamamlandığında bir kez entegre edilir.
- [x] 2B kimyasal difüzyon çekirdeğinin salım anı tekilliği pozitif başlangıç yaşıyla düzenlendi.
- [x] Kimyasal kaynak temizliği eklendi; uzaydaki merkez-yoğunluk üst sınırıyla silinen kaynakların toplam olası alan hatası tolerans altında tutulur.
- [x] Gecikmiş ödül/ceza, zaman damgalı uygunluk değişimleriyle birlikte zaman boyunca entegre edilir; nöron yeniden ateşlenmese bile çalışma dilimi sonunda işlenir.
- [x] Sinaptik etkinlik katsayısı işaretli [-2, 2] aralığına alındı; Hebbian güçlenme/STDP zayıflaması işareti korur, modülatör etkisi işaret değiştirebilir.
- [x] Yeni davranışlar için regresyon testleri eklendi.
- [x] İşaretli sinaptik ağırlık aralığına göre eski STDP alt-sınır testi düzeltildi; negatif ağırlıkta LTD'nin işareti koruması için regresyon testi eklendi.
- [x] Dallanmış feedback için aktif/pasif eşik yönü, nedensel önceki nörona yayılım ve döngü koruması testleri eklendi.
- [x] Nöron-yerel uzun dönem etkinlik izi ve yavaş ateşlenme eşiği homeostazı mevcut mekanizmaya bağlandı.
- [x] Simülasyon zamanı ilerlediğinde sessiz nöronların da homeostaz güncellemesi yapması sağlandı; Beyin yalnızca zaman bilgisini yerel nörona iletiyor.
- [x] Episode sınırında uzun dönem homeostatik etkinlik izi korunup geçen süre kadar sönümleniyor.
- [x] Homeostaz için sessiz, aşırı etkin, hedefe yakın etkinlik, episode kalıcılığı, sinaptik parametreleri koruma ve ablasyon testleri eklendi.
- [x] Seed'li, 2B uzamsal ve seyrek başlangıç ağı kurucusu eklendi; topoloji ve başlangıç parametreleri seed ile tekrarlanabilir.

## Henüz tamamlanmayan sprint başlıkları

- Seed'li seyrek ağ kurucunun kapsamlı yapılandırma, erişilebilirlik ve istatistik raporları.

- Feedback'in çoklu dal, döngü, gecikme, iz eşiği ve pozitif/negatif yönlerde kapsamlı davranış doğrulaması.
- Bağlantısız nöron toparlanması, otomatik büyüme zamanlaması ve onarım kalibrasyonu.
- Davranışsal örüntü geri çağırma, genelleme ve matematik görevleri.
- Ablasyon, çoklu seed kalibrasyonu ve ölçek ölçümleri.

## Aşama 15 — Homeostaz durumu

- Nöronun uzun dönem ateşlenme izi ve yavaş eşik kayması yerel olarak güncellenir.
- Simülasyon zamanı ilerlediğinde sessiz nöronlar da güncellenir; Beyin yalnızca zaman koordinasyonunu sağlar.
- Homeostaz yalnızca nöron ateşlenme eşiğini değiştirir; belirli öğrenilmiş sinaptik ağırlıkları veya dendrit katkılarını doğrudan değiştirmez.
- Episode geçişi uzun dönem homeostatik izi silmez; zamanla doğal sönüm devam eder.
- Hedefe yakın etkinlik, aşırı etkinlik, sessizlik, episode kalıcılığı, sinaptik parametrelerin korunması ve homeostaz ablasyonu için testler eklendi.
- Metaplastisite veya sinaptik ölçekleme eklenmedi; mevcut eşik homeostazının görevlerde yetersiz kaldığı gösterilmeden yeni mekanizma eklenmeyecek.

## Doğrulama durumu

Önceki kullanıcı doğrulamasında mevcut test paketi geçti. Bu güncellemede eklenen homeostaz testleri ve zaman/episode değişiklikleri henüz çalıştırılmadı; yeni değişiklikler yeşil kabul edilmemelidir. GitHub Actions son denemelerinde job kayıtları `steps=null` ve `logs_url=null` döndü; bu nedenle uzaktaki başarısızlıkların Python test hatası olduğu doğrulanamadı.


## Aşama 16 — İlk kontrollü geri çağırma deneyi

- `HafizaDeneyi` eklendi: ayrı eğitilmemiş baseline ağı, zayıf A→B/A→C bağlantılarıyla eğitim ağı ve eğitim sonrası yalnızca A ipucuyla geri çağırma.
- Eğitim sırasında A önce etkinleşir; B ve C daha sonra duyusal öğretim girdisi alır. Postsinaptik ateşlenmeler, mevcut yerel Hebbian mekanizmayla A çıkış bağlantılarını güçlendirir.
- Sonraki episode'da yalnızca A sunulur. B ve C'nin ağa gömülü bir örüntü tamamlama algoritması olmadan etkinleşip etkinleşmediği ölçülür.
- Başlangıç/öğrenilmiş ağırlıklar ve baseline/eğitim/geri çağırma çıktıları raporlanır.
- İki test eklendi: kısmi ipucuyla geri çağırma ve tekrarlanabilirlik.
- **Durum:** Kod ve testler eklendi; testler henüz çalıştırılmadı. Bu tek örüntülü kontrollü prototip genel hafıza, gürültü toleransı veya çoklu örüntü ayrımı kanıtı değildir.


## Aşama 16 — Ortak elemanlı örüntüler ve karışma deneyi

- `CakisikHafizaDeneyi` eklendi: A→B,C ve D→B,E ilişkileri aynı ağda ayrı episode'larda öğretiliyor; B ortak eleman.
- A ve D için ayrı eğitilmemiş baseline ağları ölçülüyor.
- Öğrenme sonrası yalnızca A veya yalnızca D ipucu sunuluyor; doğru ortak/özel elemanların geri çağrılması ve karşı örüntünün özel elemanlarının yanlış pozitif olarak etkinleşmemesi ölçülüyor.
- Dört sinaptik bağlantının başlangıç ve öğrenilmiş ağırlıkları ayrı raporlanıyor.
- Üç test eklendi: iki örüntünün ayrıştırılması, dört bağlantının da öğrenilmesi ve tekrarlanabilirlik.
- **Durum:** Kod ve testler eklendi; yerel çalıştırma bekleniyor. Bu deney yönlü ve önceden kurulmuş bağlantılarla sınırlı; aynı ipucuna bağlı çelişkili örüntü seçimi veya genel hafıza kapasitesi kanıtı değildir.


## Aşama 16 — Bağlama duyarlı geri çağırma deneyi

- `BaglamaDuyarliHafizaDeneyi` eklendi: A+X→B,C ve A+Y→D,E.
- A ipucu iki önceden kurulmuş bağlam kapısına düşük şiddetle gelir; bağlam girdisi yalnızca ilgili kapıya ek katkı sağlar.
- Tek başına A, X veya Y'nin kapı eşiğini aşmaması; iki girdinin birlikte yerel membran toplamıyla ilgili kapıyı ateşlemesi ölçülür.
- Gx ve Gy'nin ayrı çıkış bağlantıları hedef örüntülerin duyusal öğretimi sırasında yerel Hebbian öğrenmeyle güçlendirilir.
- Eğitim sonrası aynı A ipucunun X ve Y bağlamlarında farklı hedefleri geri çağırması ve karşı yolun sessiz kalması sınanır.
- Dört test eklendi: tekil girdi negatif kontrolleri, bağlama göre seçici geri çağırma, dört bağlantının öğrenilmesi ve tekrarlanabilirlik.
- **Sınır:** Bağlam kapıları ve duyusal yakınsama topolojisi deney için önceden kuruludur. Bu deney kapı/topoloji oluşumunun kendiliğinden öğrenildiğini kanıtlamaz; mevcut membran toplaması ve öğrenilmiş çıkış bağlantılarının bağlam seçiciliğine yeterli olup olmadığını sınar.


## Aşama 16 — Bağlama duyarlı geri çağırmada genlik gürültüsü

- Eğitimden sonra A ipucu ve X/Y bağlam girdilerinin genliği birlikte ölçeklenerek geri çağırma dayanıklılığı taranıyor.
- Her ölçek ve bağlam için ağ yeniden kurulup aynı iki örüntüyle eğitiliyor; böylece bir test episode'undaki yerel plastisite başka bir test koşulunu kirletmiyor.
- ±%5 genlik değişiminde iki bağlamın doğru örüntüyü koruması, eşik altı %10 azaltımda ise kapıların sessiz kalması denetleniyor.
- **Sınır:** Bu, giriş genliğine karşı kontrollü dayanıklılık ölçümüdür; eksik duyusal kanal, rastgele gürültü dağılımı veya kendiliğinden öğrenilmiş bağlam kapısı kanıtı değildir.


## Aşama 16 — Bağımsız ipucu/bağlam genliği taraması

- Önceki tarama hem A ipucunu hem X/Y bağlam girdisini aynı katsayıyla değiştiriyordu. Bu, hangi kanalın eşik davranışını belirlediğini ayırt etmiyordu.
- Yeni deney ipucu ve bağlam genliğini bağımsız değiştirir; her koşulda tek ağda iki örüntü yeniden öğretilir ve iki bağlam da geri çağrılır.
- %10 azaltımın yalnızca bir kanala uygulanması ile iki kanala birlikte uygulanması karşılaştırılır.
- Bu deney rastgele gürültü veya eksik kanal toleransı değil, kanal bazında genlik duyarlılığı ölçümüdür.


## Aşama 16 — bağlama duyarlı geri çağırma: rastgele gürültü ve kanal kaybı

- Bağımsız genlik taramasından sonra iki ayrı bozulma türü eklendi.
- Rastgele genlik gürültüsü, temiz eğitimden sonra yalnızca geri çağırma ipucu ve bağlam girdilerine bağımsız Gauss pertürbasyonu uygular. Her tekrar temiz eğitilmiş yeni bir ağdan başlar; seed ile tekrarlanabilirlik, tam eşleşme oranı, yanlış pozitifler ve ortalama olay sayısı raporlanır.
- Eksik kanal deneyi, geri çağırma sırasında ipucunu veya bağlamı tamamen kaldırır. Beklenti, tek başına kalan kanalın kapıyı ateşlememesi ve yanlış örüntü üretmemesidir.
- Bu deneyler henüz kullanıcı tarafından çalıştırılmadı; sonuç veya dayanıklılık iddiası yoktur.


## Aşama 16 — gürültü kaynağını kanala göre ayırma

- Önceki rastgele gürültü deneyi ipucu ve bağlam genliklerini aynı anda bozuyordu; tek başına hangi kanalın kırılgan olduğu ayırt edilemiyordu.
- Yeni `kanal_bazli_gurultu_taramasi` gürültüyü yalnızca ipucu kanalına, yalnızca bağlam kanalına veya iki kanala birlikte uygular.
- Varsayılan tekrar sayısı 100'dür; oran, kanal, seed ve tekrar sayısı parametrelenebilir.
- Her kanal/şiddet/bağlam için tam eşleşme oranı, yanlış pozitif sayısı ve ortalama olay sayısı raporlanır.
- Bu aşama önceden kurulmuş küçük bağlam kapıları üzerinde dayanıklılık ölçümüdür; kendi kendine bağlam topolojisi öğrenildiğini göstermez.


## Aşama 16 — çoklu seed ile gürültü dayanıklılığı doğrulaması

- Kanal bazlı taramada ipucu, bağlam ve birleşik gürültü ayrı ayrı ölçüldü. 100 tekrar/koşul sonuçlarında yanlış pozitif görülmedi; gürültü arttıkça tam eşleşme düştü.
- Tek seed'e özgü rastlantıyı değerlendirmek için `coklu_seed_gurultu_ozeti` eklendi. Varsayılan üç bağımsız seed'in sonuçlarını birleştirir; toplam başarı oranının yanında seed başına oranların en düşüğünü ve en yükseğini verir.
- Bu özet son doğrulama içindi. Çoklu-seed sonuçları alındı ve aşağıdaki tabloda kaydedildi; bağlama duyarlı hafıza prototipi donduruldu. Mevcut deney genel hafıza veya kendiliğinden bağlam kapısı oluşumunu kanıtlamaz.


## Aşama 16 — Bağlama duyarlı hafıza son doğrulaması

- Üç seed ve seed başına 100 tekrar ile kanal bazlı gürültü taraması tamamlandı; her koşul X/Y için 300 deneme içeriyor.
- İpucu gürültüsünde tam eşleşme: %5 düzeyinde X %100 / Y %99,3; %10'da X %92,7 / Y %92; %20'de X %74,3 / Y %72,7.
- Bağlam gürültüsünde tam eşleşme: %5 düzeyinde X %99 / Y %99,3; %10'da X %90 / Y %89,7; %20'de X %71,3 / Y %72,7.
- İki kanala birlikte gürültüde tam eşleşme: %5 düzeyinde X %95,3 / Y %96; %10'da X %82 / Y %77; %20'de X %66 / Y %66,7.
- Bütün koşullarda yanlış pozitif sayısı 0.
- **Karar:** Bağlama duyarlı hafıza doğrulama ailesi donduruldu; yeni gürültü kombinasyonları eklenmeyecek. Bu sonuç küçük ve önceden kurulmuş bağlam kapılı ağla sınırlıdır.

## Aşama 17 — Sayısal temsil altyapısı

- [x] SayisalTemsil.py eklendi: 1–9 aralığı için log-Gauss ayarlı, örtüşen popülasyon kodlaması.
- [x] İdeal popülasyon yanıtları, her birim için zamansal duyusal darbe sayılarına çevriliyor.
- [x] MotorOrgan.ateslenme_sayilari_oku ile episode içindeki gerçek spike sayıları okunabiliyor; mevcut ikili oku arayüzü korunuyor.
- [x] Popülasyon örüntüsü, sabit kod kitabına göre harici motor çözücüden sayısal etikete dönüştürülebiliyor.
- [x] Temsil, örtüşme, ayırt edilebilirlik, geçersiz girdi ve gerçek Beyin spike döngüsü üzerinden gidiş-dönüş testleri eklendi.
- **Sınır:** Bu sabit duyusal kodlayıcı, sayısal büyüklükleri ağ için önceden popülasyon örüntüsüne dönüştürür. Henüz ağın kendi kendine sayı kavramı veya aritmetik öğrendiği anlamına gelmez. Sıfır ayrıca temsil edilmemiştir.
- **Doğrulama:** Testler depoya eklendi; bu güncellemede yerel pytest çalıştırılmadı. Kullanıcı ortamında çalıştırılmalıdır.



## Aşama M1 — Büyüklük karşılaştırması (ilk deney düzeneği)

- `M1_BuyuklukKarsilastirma.py` eklendi.
- Sol ve sağ sayılar, mevcut 1–9 popülasyon kodlayıcısıyla iki ayrı duyusal kanala sunulur.
- Her duyusal nöron iki karar nöronuna da rastgele işaretli projeksiyon yapar. Başlangıç bağlantı düzeni sayısal büyüklük veya doğru cevap bilgisi içermez.
- Karar nöronları arasında sabit karşılıklı inhibisyon, genel bir rekabet/WTA mekanizması olarak kullanılır; karşılaştırma kuralını kodlamaz.
- Görev ortamı doğru/yanlış değerlendirmesinden sonra yalnızca kimyasal `odul` veya `ceza` kaynağı bırakır. Doğru kararda ödül doğru çıktı bölgesine, yanlış kararda ceza ateşlenen yanlış çıktı bölgesine salınır. Girdi sinapslarının terminal konumları hedef karar bölgesindedir; uzamsal difüzyon böylece modülatörü ilgili bağlantı grubuna sınırlar.
- Görev ortamı sinaptik ağırlıkları doğrudan değiştirmez; mevcut yerel uygunluk izi ve gecikmiş modülatör mekanizması güncellemeyi yapar. Karar çıkmadığında yanlış bir yol belirlenemediği için kimyasal ceza salınmaz.
- Eğitim/test ayrımı sırasız sayı çiftleri üzerinden yapılır. Örneğin (2,7) eğitimdeyse (7,2) de eğitimdedir; ters sıralı çift testte tutulamaz.
- Test ölçümü karar doğruluğunun yanında iki karar nöronunun birlikte ateşlenmesini, hiçbirinin ateşlenmemesini ve kararsız çıktıyı raporlar.
- **Sınır:** Bu yalnızca ilk öğrenme deney düzeneğidir. Ağın büyüklük karşılaştırmasını öğrendiği veya görülmemiş çiftlere genellediği henüz gösterilmiş değildir. İlk kullanıcı çalıştırması öncesinde başarı iddiası yoktur.


### M1 — Davranış ve ağırlık tanılaması

- `M1_Tanilama.py` genişletildi: eğitim/test karar dağılımı (SOL/SAG/kararsız), beklenen sınıfa göre ayrı doğruluk ve hedef karar nöronuna göre duyusal ağırlık dağılımları raporlanır.
- Duyusal projeksiyon ağırlıkları, sabit WTA bağlantılarından ayrı raporlanır. Önceki tanılamada 38 bağlantı tek grup gibi gösteriliyordu; bunun 36 duyusal projeksiyon + 2 WTA bağlantısından oluştuğu ayrıştırıldı.
- Tanılama testleri eklendi. Yerel pytest bu işlem sırasında çalıştırılmadı.
- Amaç: tek karar tarafına yanlılık, sınıf bazlı öğrenme başarısızlığı ve ağırlık değişiminin hangi karar popülasyonunda toplandığını birbirinden ayırmak.


### M1 tanılama genişletmesi — işaretli projeksiyon ve gerçek terminal akışı

- Baglanti.iletim_etkisi() doğrulandı: iletilen sinaptik katsayı tam olarak etki × sinaptik_agirlik × yapisal_olgunluk.
- Önceki raporda yalnızca sinaptik_agirlik pozitif görünüyordu. Bu, uyarıcı/baskılayıcı ayrımını göstermiyordu; çünkü başlangıç işareti etki içinde tutuluyor. Yeni tanılama artık imzalı gerçek iletim katsayısını ve kaynak dendritin sinapsa verdiği katkıyı ayrı raporluyor.
- Eğitim boyunca her örnekte terminal aktivasyon sayısı farkı ölçülüyor; bu sayı imzalı iletim katsayısıyla çarpılarak kanal→karar hedefi bazında yaklaşık sinaptik olay akışı hesaplanıyor. Ayrıca sol/sağ duyusal nöronların ateşlenmeleri terminal aktivasyonlarından ayrı tutuluyor.
- Bu akış toplamı hedef nöron membran potansiyeli değildir; hedefe zamanlanan imzalı sinaptik olayların tanısal yaklaşık toplamıdır. Öğrenme mekanizmasına müdahale etmez.
- Yeni testler imzalı katsayı formülünü, dendrit katkısını ve aktivasyon farkı hesabını kontrol eder.


## Aşama M2 — BrainOld tarzı binary giriş ve ara nöron katmanı

- `M2_BinaryBuyuklukKarsilastirma.py` eklendi: 1–9 aralığındaki sayılar dört bitlik binary kodla temsil edilir.
- BrainOld'daki reseptör düzenine yaklaştırıldı: sol ve sağ operand için **iki reseptör nöronu**, her birinde dört bit dendriti bulunur. Böylece 8 bit kanalı yalnızca 2 duyusal nöronun dendritleri üzerinden sunulur.
- Ağda 2 reseptör, 20 ara ve 2 karar nöronu olmak üzere toplam 24 nöron vardır. Her reseptör nöronundan her ara nörona bir terminal gider; bu terminal dört bit dendritinin ayrı ve işaretli katkılarını toplar.
- Her ara nöron sol ve sağ reseptörden birer dendritik girdi alır ve iki karar nöronuna projekte olur. Reseptörlerden karar nöronlarına doğrudan bağlantı yoktur.
- Reseptör→ara bağlantılar yerel Hebbian/STDP plastisitesine; ara→karar bağlantıları gecikmiş yerel ödül/ceza modülatörüne açıktır. Görev ortamı ağırlıkları doğrudan değiştirmez.
- Test örnekleri, eğitim sonrası ağın bağımsız kopyalarında tek tek değerlendirilir. Böylece test örnekleri birbirlerinin parametrelerini değiştirmez; eğitimden kalan kimyasal kaynaklar test kopyasından temizlenir.
- Tanılama, karar dağılımını ve beklenen sınıfa göre doğruluğu ayrı raporlar; sinaptik ağırlık değişimini reseptör→ara ve ara→karar grupları için ayrı özetler.
- Testler binary kodlamayı, bit-dendrit olaylarını, ağ boyutunu, bağlantı yönlerini, seed tekrarlanabilirliğini, eğitim/test ayrımını, tanılama özetlerini ve test kopyalarının eğitim ağını değiştirmediğini denetler.
- **Sınır:** Bu yeni deney henüz kullanıcı ortamında çalıştırılmadı. Ara katman ve BrainOld tarzı binary giriş eklendi; karşılaştırma başarısı veya genelleme iddiası yoktur. İlk çalıştırmada eğitim/test davranışı, sınıf yanlılığı ve öğrenilen bağlantı değişimleri birlikte incelenmelidir.


## M2 — katman-katman pasif tanilama

- Nöronlara episode başına pasif tanılama sayaçları eklendi: entegrasyon sayısı, işaretli/mutlak membran girdisi, en yüksek tek entegrasyon girdisi, görülen maksimum membran ve eşik marjı.
- Sayaçlar episode başında sıfırlanır; öğrenilmiş parametrelere ve ağ davranışına müdahale etmez.
- `BrainNew/M2_Tanilama.py` eğitim örneklerini tek tek çalıştırıp reseptör, ara ve karar katmanlarının toplam ateşlenme/entegrasyon verilerini; sinaps terminal aktivasyonlarını ve modülatör değişimlerini raporlar.
- `BrainNew/tests/test_neuron_episode_diagnostics.py` tanılama sayaçlarının hesaplanmasını ve episode resetini kapsar.
- Henüz pytest çalıştırılmadı; kullanıcı yerel ortamında odaklı ve tam testleri çalıştırmalı.
