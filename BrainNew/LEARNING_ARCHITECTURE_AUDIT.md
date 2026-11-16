# BrainNew — Öğrenme Mimarisi Denetimi ve Veri Sözleşmesi

Durum: Aktif `fix/brainnew-architecture-audit` dalındaki güncel uygulama; yerel Hebbian/STDP ve gecikmiş modülatör/uygunluk izi katmanlarını içerir.
Dal: `fix/brainnew-architecture-audit`
İlgili sprint: `LEARNING_SPRINT.md`

## 1. Denetim kapsamı

Güncel dalda `Baglanti.py`, `Beyin.py`, `Dendrid.py`, `Noron.py`, `KimyasalAlan.py`, deney sürücüsü ve elektriksel testler incelendi. Bu belge eski `experiment/dendritic-synaptic-potentials` dalının durumunu değil, aktif dalın mevcut kodunu tanımlar.

## 2. Mevcut değişkenlerin gerçek anlamı

| Değişken | Kodda şu anki işlevi | Sahibi | Ömrü | Kalıcı öğrenme mi? |
|---|---|---|---|---|
| `Baglanti.potansiyel` | Dendritik iç-yönlendirme sinyaliyle değişen, terminalin ateşleme anında hazır olup olmadığını belirleyen yerel durum | Baglanti | Kısa; `sonum_tau` ile sıfıra sönümlenir | Hayır |
| `Baglanti.esik` | Terminalin aktive edilmeye uygunluk eşiği | Baglanti | Sabit parametre | Şu an hayır |
| `Baglanti.etki` | Gerçek pre→post iletim olayının işaretli temel etki miktarı | Baglanti | Bağlantı ömrü | Hayır |
| `Baglanti.sinaptik_agirlik` | Temel elektriksel etkiyi ölçekleyen kalıcı, sınırlı katsayı | Baglanti | Bağlantı ömrü | Evet; yerel Hebbian güncellemesi var |
| `Baglanti.iz` | Aktivasyonla artan ve sönümlenen kullanım/bakım izi | Baglanti | Geçici, `sonum_tau` ile sönümlenir | Hayır |
| `Baglanti.pre_iz` | Kaynak terminal aktive olduğunda artan, üstel sönümlü presinaptik etkinlik izi | Baglanti | Kısa | Hayır |
| `Baglanti.post_iz` | Hedef nöron ateşlendiğinde artırılan postsinaptik iz | Baglanti | Kısa | Hayır |
| `Dendrid.sinaps_katkilari[s]` | Bir dendritin, aynı nöronun çıkış terminali hazır olma potansiyeline katkısı | Dendrid | Öğrenmeyle değişebilir | Evet; fakat yalnızca nöron-içi yönlendirme parametresi |
| `Dendrid.sinaps_degerlendirmeleri` | Katkı değerlendirme sayacı; sonraki dendrit katkı güncellemesinin yerel bağlamını tutar | Dendrid | Dendrit durumu boyunca | Doğrudan ağırlık değil |
| `Baglanti.yapisal_butunluk` | Bağımsız mikroglia ajanlarının değerlendirdiği yapısal durum | Baglanti | Uzun | Yapısal durum; iletim ağırlığı değil |
| `KimyasalAlan` kaynakları | Salım konumu, zamanı, miktarı ve yayılım/temizlenme bilgisi | KimyasalAlan | Kaynağın zaman profiline bağlı | Hayır |

**Önemli ayrım:** `potansiyel`, `etki`, `iz`, `pre_iz` ve `post_iz` birbirinin yerine kullanılamaz. Kodda aynı isim ailesine ait olmaları aynı fiziksel/hesaplamalı anlamı taşıdıkları anlamına gelmez.

## 3. İki farklı topoloji katmanı

### 3.1 Gerçek biyolojik-esinli pre→post bağlantı

`Baglanti.kaynak`, `Baglanti.hedef` ve `hedef_dendrit_id` yönlü iletim kenarını tanımlar. Kaynak nöronun ateşlenmesi terminali aktive eder; olay gecikmeyle hedef nöronun belirtilen dendritine iletilir. `Baglanti.etki` bu hedef girdinin sabit büyüklüğüdür.

Bu gerçek bağlantı için ayrı kalıcı elektriksel katsayı `sinaptik_agirlik` eklendi. İletilen elektriksel etki `etki * sinaptik_agirlik` olur. Katsayı [0,2] aralığındadır ve şu an yalnızca açıkça ayarlanan parametredir; henüz otomatik öğrenilmez. Kimyasal transmitter salımı bu katsayıyla ölçeklenmez. Bu nedenle mevcut kod gerçek pre→post sinaptik ağırlık öğreniyor diye raporlanamaz.

### 3.2 Nöron-içi dendrit→çıkış-terminali yönlendirmesi

`Dendrid.sinaps_katkilari`, aynı nöronun dendritik girdisinin kendi çıkış terminallerinin geçici hazır olma potansiyelini nasıl etkileyeceğini tanımlar. `Noron.girdileri_birlestir` katkıları sinaps bazında birleştirir ve `Baglanti.potansiyel` değerini günceller. `Dendrid.firsat_sonucu_ogren` bu katkıları yerel ateşlenme sonucuna göre değiştirir.

Bu, mevcut simülatörde çalışan bir nöron-içi hesaplamalı yönlendirme öğrenmesidir. Gerçek pre→post sinaptik plastisite değildir ve ayrı ölçülmelidir.

## 4. Bağlantı-seçici pre/post izleri ve Hebbian güncellemesi

İzlerin ve olay atfının güncel yaşam döngüsü:
- `pre_iz`, kaynak bağlantı aktive olduğunda `Baglanti.aktive_et(zaman)` içinde artar.
- Kaynak bağlantı kimliği, iletim olayı boyunca hedef dendrite taşınır.
- Hedef nöronun entegrasyonu, o entegrasyona kaynak olmuş bağlantıları yerel olarak kaydeder.
- Hedef ateşlenirse yalnızca bu bağlantıların Hebbian güncellemesi ve postsinaptik izi işlenir.
- Her iki iz de kendi zaman sabitiyle üstel olarak sönümlenir.
- Beyin bağlantı seçmez ve ağırlık güncellemesini hesaplamaz.

İlk bağlantı-yerel Hebbian kuralı uygulanmıştır:
`Δw = η_H · pre_iz · (w_max - w)/(w_max - w_min)`

Bu kural, pre→post sıralamasında pozitif ağırlık değişimi üretir. Ayrıca ters post→pre sıralamasında, presinaptik olay geldiğinde mevcut post izine bağlı LTD uygulanır. Bu çift-izli STDP prototipidir; uygunluk izi/modülatör kapısı ve görev başarısı ölçümü henüz yoktur. Dolayısıyla genel öğrenme kapasitesinin kanıtı değildir.

### Gerekli düzeltme sözleşmesi

1. Sinaptik girdi olayı, kaynak `Baglanti` kimliğini hedef dendrite kadar taşımalıdır.
2. Hedef dendrit, o entegrasyonda hangi kaynak sinaptik olayların işlenmiş olduğunu yerel olarak kaydetmelidir.
3. Hedef nöron ateşlenirse yalnızca ilgili entegrasyona katkı vermiş bağlantılar postsinaptik olay/iz almalıdır.
4. Hedef nöron ateşlenmezse olayın yerel dendritik yanıtı ile sonraki ateşlenmeler birbirine yanlışlıkla bağlanmamalıdır; geçici uygunluk/olay bağlamının ömrü açıkça tanımlanmalıdır.
5. Aynı zaman damgasındaki olaylar mevcut deterministik olay sırasını korumalıdır.
6. Beyin bağlantı seçimi veya plastisite kararı vermemeli; yalnızca kaynak olay bilgisini hedef yerel bileşene taşımalıdır.

## 5. Öğrenilebilir parametrelerin tek sahipliği

| Öğrenilebilir durum | Tek güncelleme sahibi | Güncelleme tetikleyicisi | Sınır/ömür |
|---|---|---|---|
| Dendrit-terminal katkısı | İlgili Dendrid | Kendi yerel sinyalinin işlendiği nöron entegrasyonu ve ateşlenme sonucu | Dendritin `katki_alt`–`katki_ust` sınırları |
| Gerçek sinaptik etkinlik katsayısı | İlgili Baglanti | Şu an açık parametre ayarı; ileride doğrulanmış yerel öğrenme kuralı | [0,2] |
| Sinaptik uygunluk izi | İlgili Baglanti | Yerel pre/post sırası | Geçici, sınırlı ve sönümlü |
| Nöron homeostatik eşik kayması | İlgili Noron | Uzun dönem yerel ateşlenme etkinliği | Sınırlı ve yavaş |
| Yapısal bütünlük | İlgili Baglanti | Yerel bakım değerlendirmesi | [0,1] |

Beyin yalnızca simülasyon saatini, olay kuyruğunu ve bileşenler arası veri aktarımını yönetir. Öğrenme değişkenlerinin değerini seçmez veya hangi bağlantının değişeceğine karar vermez.

## 6. Uygulama durumu

**Kodda bulunan katmanlar**
- Geçici terminal potansiyeli ile gerçek bağlantı iletim katsayısı ayrı.
- Dendrit-terminal iç-yönlendirme katkısı ile gerçek pre→post sinaptik ağırlık ayrı.
- Kaynak bağlantı kimliği hedef dendrit entegrasyonuna kadar taşınıyor.
- Bağlantı bazında pre/post izleri, yerel Hebbian LTP ve ters sıralı STDP-LTD uygulanıyor.
- İşaretli, sınırlı ve sönümlü uygunluk izi; yerel ödül/ceza kimyasal alanıyla gecikmiş ağırlık güncellemesi ilk sürüm olarak eklendi.
- Öğrenme durumları ilgili Baglanti nesnesinde tutuluyor; nöron homeostazı ilgili Noron nesnesinde tutuluyor; yapısal bakım kararı bağımsız Mikroglia ajanlarında; Beyin yalnızca olay akışını koordine ediyor.

**Henüz doğrulanmamış noktalar**
- Gecikmiş modülatörün gerçek simülasyon olay akışında hangi sıklıkta örnekleneceği ve kısa ödül darbelerinin kaçırılma riski.
- Anlık STDP ile gecikmiş modülatör güncellemesinin birlikte çalışmasının ağ düzeyindeki etkisi.
- Parametrelerin kararlılığı, görev öğrenmesi ve genelleme.
- Uygunluk izinin biyolojik zaman ölçeği ve ödül/ceza alanlarının kalibrasyonu.

Bir değişkenin değişmesi tek başına öğrenme kanıtı sayılmaz. Bu katmanlar önce birim testleriyle, sonra ayrılmış eğitim/test deneyleriyle değerlendirilmelidir.

## 7. Sonraki kontrollü adım

Sıradaki adım, üç faktörlü öğrenme yolunu gerçek örüntü görevlerine bağlamak ve modülatörün olay akışında yeterli sıklıkta örneklendiğini doğrulamaktır. Ardından:
- homeostatik dengeleme,
- yapısal bağlantı oluşumu ve yeniden bağlantılanma,
- örüntü geri çağırma ve genelleme deneyleri,
- ablation karşılaştırmaları

kontrollü olarak ele alınacaktır.


## 8. İlk yerel Hebbian ağırlık güncellemesi

- Gerçek pre→post bağlantısının kalıcı elektriksel katsayısı `Baglanti.sinaptik_agirlik` üzerinde çalışır.
- Kaynak bağlantıdan gelen presinaptik iz, hedef nöronun o bağlantıya atfedilmiş postsinaptik ateşlenmesi sırasında okunur.
- Yerel güncelleme:

`Δw = η_H · pre_iz · (w_max - w)/(w_max - w_min)`

- Güncelleme yalnızca ilgili bağlantının pre izi pozitifse yapılır; ilgisiz gelen bağlantılar değişmez.
- Güncelleme bağlantı nesnesinin kendi metodundadır. Nöron yalnızca kendi ateşlenme olayı sırasında ilgili yerel bağlantı metodunu çağırır; Beyin öğrenme hesabı yapmaz.
- Hebbian güçlendirme STDP'nin LTP kolu olarak pre→post sıralamasında çalışır; ters post→pre sıralaması ayrı LTD kolunu tetikler.
- Bu kuralın görev genellemesi sağladığı henüz gösterilmiş değildir; yalnızca yerel eşleşme öğrenmesinin altyapısıdır.


## 10. Üç faktörlü gecikmiş modülasyon ve uygunluk izi

- Her bağlantı kendi sınırlı, üstel sönümlü `uygunluk_izi` durumunu taşır.
- Pre→post eşleşmesi pozitif; post→pre eşleşmesi negatif uygunluk üretir.
- Uygunluk tek başına ağırlığı değiştirmez.
- Bağlantı yerel bakım/etkinlik olayı sırasında terminal konumundaki kimyasal alan örneklenir: `odul - ceza`.
- Gecikmiş modülatör, yakın geçmişteki uygunluk izini ağırlık değişimine çevirir. Güncelleme örnekler arası trapez integraliyle zaman aralığına bağlanır; salt bakım çağrısı sayısına bağlanmaz.
- Bu prototipte `odul` ve `ceza` pozitif yoğunluklu ayrı kimyasal türlerdir. İşaret farktan gelir.
- Bu katman mevcut anlık STDP plastisitesine ek bir gecikmiş geri bildirim yoludur; STDP'yi henüz modülatör kapılı tek mekanizma haline getirmez.
- Parametreler ve alan yoğunlukları biyolojik kalibrasyon değildir; görev deneyleriyle ayarlanmalıdır.


## 11. Nöron-yerel homeostatik etkinlik dengelemesi

- Her nöron kendi ateşlenme etkinliği izini tutar; iz zamanla üstel olarak söner.
- Nöron, gözlenen uzun dönem etkinliği hedef etkinlikle karşılaştırır.
- Hedefin üzerinde etkinlik eşik kaymasını yükseltir; hedefin altında etkinlik eşiği düşürür.
- Eşik kayması nöronun kendi temel `esik_temel` değerine eklenir ve sınırlıdır. Başka nöronların veya Beyin'in eşiklerini değiştirmez.
- Güncelleme, geçen zaman boyunca izlenen etkinlik hatasının analitik integraline dayanır; çağrı sayısına doğrudan bağlı değildir.
- Bu ilk homeostaz biçimi ateşlenme eşiğini düzenler. İnhibitör plastisite, sinaptik ölçekleme ve metaplastisite henüz uygulanmış değildir.
- Parametreler prototip değerleridir; görev deneyleri ve ağ kararlılığı testleriyle kalibre edilmelidir.


## 12. Bağımsız mikroglia ajanı

- Mikroglia, sinapsın içine gömülü bir alan değil, bağımsız bir ajandır.
- İlk hesaplamalı modelde hücre gövdesi sabittir; algılama yarıçapı hareketli uzantıların yerel çevre taramasını soyutlar.
- Ajan, uzamsal indeks üzerinden yalnızca yakın sinapsları bulur.
- Kullanım izi, yerel büyüme/stabilizasyon/budama kimyası ve yapısal bütünlük birlikte değerlendirilir.
- Kullanılmama tek başına fiziksel kopma oluşturmaz; budama işareti ve düşük kullanım birlikte gerekir.
- Mikroglia karar verir; Beyin yalnızca bakım olayını zamanlar ve kopmuş bağlantıyı ağ kayıtlarından temizler.
- Bu model gerçek hücre morfolojisini, göçünü veya moleküler repertuvarını simüle etmez.
