# BrainNew — Öğrenme Mimarisi Denetimi ve Veri Sözleşmesi

Durum: Aktif `fix/brainnew-architecture-audit` dalı üzerinden yeniden denetlendi. Teorik sahiplik sözleşmesi güncellendi; aşağıdaki iki olay-atıf sorunu çözülmeden kalıcı plastisite uygulanmayacak.
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
| `Baglanti.yapisal_butunluk` | Bağlantı-yerel bakım/budama modelinin yapısal durumu | Baglanti | Uzun | Yapısal durum; iletim ağırlığı değil |
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

Bu kural, nedensel pre/post eşleşmesinde pozitif ağırlık değişimi üretir ve üst sınıra yaklaştıkça küçülür. Henüz ters zaman sırasına bağlı zayıflatma, uygunluk izi/modülatör kapısı veya görev başarısı ölçümü yoktur. Dolayısıyla bu aşama STDP ya da genel öğrenme kapasitesinin kanıtı değildir.

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
| Sinaptik uygunluk izi (henüz eklenmedi) | İlgili Baglanti | Bağlantıya nedensel olarak atfedilmiş pre/post etkinlik | Geçici, sönümlü |
| Nöron homeostatik durumu (henüz eklenmedi) | İlgili Noron | Uzun dönem yerel etkinlik ölçümü | Sınırlı ve yavaş |
| Yapısal bütünlük | İlgili Baglanti | Yerel bakım değerlendirmesi | [0,1] |

Beyin yalnızca simülasyon saatini, olay kuyruğunu ve bileşenler arası veri aktarımını yönetir. Öğrenme değişkenlerinin değerini seçmez veya hangi bağlantının değişeceğine karar vermez.

## 6. Aşama 1 sonucu

**Tamamlanan teorik ayrımlar**
- Geçici terminal potansiyeli ile gerçek bağlantı iletim etkisi ayrı.
- Dendrit-terminal iç-yönlendirme katkısı ile gerçek pre→post bağlantı öğrenmesi ayrı.
- Kullanım izi, pre/post izleri ve ilerideki uygunluk izi ayrı işlevler.
- Kalıcı parametrelerin tek bir yerel güncelleme sahibi olması ilkesi tanımlı.

**Kodda henüz sağlanmayan koşullar**
- Gerçek sinaptik etkinlik katsayısı eklendi; otomatik plastisite kuralı henüz yok.
- Sinaptik olayın kaynak bağlantı kimliği hedef dendrit entegrasyonuna kadar taşınmıyor.
- Postsinaptik iz bütün gelen bağlantılara artırılıyor; yalnızca gerçekten katkı veren bağlantılarla sınırlandırılmalı.
- Pre/post izleri mevcut olsa da bunlar henüz güvenilir, bağlantı-seçici STDP altyapısı değildir.

Bu nedenle Aşama 1'in veri sözleşmesi netleşmiştir; fakat pre/post izlerinin olay-atıf kısmı uygulama düzeyinde tamamlanmış sayılmaz.

## 7. Sonraki kontrollü adım

Bir sonraki kod adımı kalıcı ağırlık veya STDP eklemek değildir. Önce sinaptik olay kimliğinin hedef dendrite taşınması ve yalnızca ilgili bağlantıların yerel postsinaptik olayla eşleştirilmesi uygulanıp test edilecektir. Ardından:
- bağlantı-seçici pre/post izleri,
- gerçek sinaptik etkinlik katsayısı,
- STDP/Hebbian güncellemesi,
- gecikmiş modülatör/uygunluk izi

sırasıyla ele alınacaktır.

Her aşamada testler, eğitim/test ayrımı ve olay sırası korunur. Bir değişkenin değişmesi tek başına öğrenme kanıtı sayılmaz.


## 8. İlk yerel Hebbian ağırlık güncellemesi

- Gerçek pre→post bağlantısının kalıcı elektriksel katsayısı `Baglanti.sinaptik_agirlik` üzerinde çalışır.
- Kaynak bağlantıdan gelen presinaptik iz, hedef nöronun o bağlantıya atfedilmiş postsinaptik ateşlenmesi sırasında okunur.
- Yerel güncelleme:

`Δw = η_H · pre_iz · (w_max - w)/(w_max - w_min)`

- Güncelleme yalnızca ilgili bağlantının pre izi pozitifse yapılır; ilgisiz gelen bağlantılar değişmez.
- Güncelleme bağlantı nesnesinin kendi metodundadır. Nöron yalnızca kendi ateşlenme olayı sırasında ilgili yerel bağlantı metodunu çağırır; Beyin öğrenme hesabı yapmaz.
- Bu ilk Hebbian katman yalnızca pozitif birliktelik güçlendirmesidir. Nedensel zaman sırası ve ters sıra zayıflatması henüz STDP aşamasına aittir.
- Bu kuralın görev genellemesi sağladığı henüz gösterilmiş değildir; yalnızca yerel eşleşme öğrenmesinin altyapısıdır.
