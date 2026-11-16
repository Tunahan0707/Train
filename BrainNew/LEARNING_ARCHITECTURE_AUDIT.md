# BrainNew — Öğrenme Mimarisi Denetimi ve Veri Sözleşmesi

Durum: Aşama 1 teorik denetimi tamamlandı; kod değişikliği yapılmadı.
Dal: `experiment/dendritic-synaptic-potentials`
İlgili sprint: `LEARNING_SPRINT.md`

## 1. Denetlenen mevcut bileşenler

Denetim, sprint dalındaki mevcut `Baglanti.py`, `Beyin.py`, `Dendrid.py`, `Noron.py`, `KimyasalAlan.py` ve test dosyalarına dayanır. Bu dalın mevcut içeriği, önceki konuşmada incelenmiş `fix/brainnew-architecture-audit` dalındaki bazı değişikliklerle aynı değildir. Özellikle bu sprint dalındaki `Baglanti.py` şu anda yerel mikroglia-benzeri bakım veya dendritik transmitter salım modülasyonu içermiyor. Bu nedenle bu özellikler uygulanmış kabul edilmemelidir.

## 2. Mevcut durumun gerçek anlamı

### 2.1 `Baglanti` içindeki `potansiyel`

- `potansiyel`, şu anki kodda kalıcı öğrenilmiş sinaptik etkinlik/ağırlık değildir.
- Dendritlerden gelen yerel sinyaller `etki_uygula` üzerinden bu değeri değiştirir.
- Değer eşik ile karşılaştırılarak çıkış terminalinin aktive olup olmayacağı seçilir.
- Zamanla `sonum_tau` ile sıfıra sönümlenir.
- Dolayısıyla bu değişken en doğru biçimde **geçici terminal hazır olma/aktivasyon durumu** olarak adlandırılmalıdır.

### 2.2 `Baglanti.etki`

- `etki`, sinaptik iletim olayında hedef dendrite verilen etkinin sabit büyüklüğüdür.
- Şu anda öğrenme tarafından güncellenmez.
- Bu, ileride eklenecek kalıcı sinaptik etkinlik katsayısı ile aynı şey değildir.

### 2.3 `Baglanti.iz`

- `aktive_et` sırasında artar ve `sonum_tau` ile sönümlenir.
- Mevcut kodda bir kullanım/aktivasyon izi başlangıcıdır.
- Henüz pre/post eşleşmesini, nedensel zaman farkını veya gecikmiş geri bildirim uygunluğunu temsil etmez.
- Yeni öğrenme mimarisinde bu iz, açıkça tanımlanmış kullanım izi ve sinaptik uygunluk iziyle birleştirilmemelidir.

### 2.4 `Dendrid.sinaps_katkilari`

- Dendrit, bu sözlükteki `Baglanti` nesnelerini kendi yerel sinyaliyle etkiler.
- `Noron.girdileri_birlestir` bu katkıları toplar, sinaps başına karekök normalizasyonu yapar ve bağlantının geçici potansiyelini değiştirir.
- `firsat_sonucu_ogren`, yalnızca gerçekten katkı yüklemiş dendrit-sinaps çiftlerinin katkı değerini günceller.
- Bu eşleme, mevcut simülatörün **nöron içi dendrit → çıkış terminali hazırlama soyutlamasıdır**. Gerçek biyolojik pre→post sinapsın postsinaptik dendrit girdisiyle aynı bağlantı nesnesi değildir.
- Mevcut güncelleme, bu iç-yönlendirme katkısının küçük artış/azalışıdır; gerçek sinaptik ağırlık plastisitesi olarak raporlanmamalıdır.

### 2.5 Gerçek bağlantı topolojisi

- `Baglanti.kaynak`, `Baglanti.hedef` ve `hedef_dendrit_id` gerçek yönlü iletim kenarını tanımlar.
- Beyin, kaynak nöron ateşlenmesi sonrasında bağlantıyı aktive eder ve hedef nöronun hedef dendritine gecikmeli girdi olayı gönderir.
- Bu yönlü kenar üzerinde henüz ayrı bir kalıcı sinaptik etkinlik ağırlığı, pre/post iz çifti veya uygunluk izi bulunmamaktadır.
- Bu nedenle gerçek bağlantı öğrenmesi henüz uygulanmış değildir.

## 3. Öğrenme mimarisi için değişken sahipliği

| Değişken | Anlam | Sahibi | Zaman ölçeği | Kalıcı mı? |
|---|---|---|---|---|
| Terminal hazır olma potansiyeli | Çıkış terminalinin o an aktive olmaya yatkınlığı | Baglanti | Kısa | Hayır |
| Dendrit-terminal katkısı | Dendritik yerel sinyalin terminal hazır olmasına etkisi | Dendrid | Öğrenmeyle değişebilir | Evet, iç-yönlendirme parametresi |
| Sinaptik etkinlik katsayısı | Gerçek pre→post bağlantının iletim etkisi | Baglanti | Uzun | Evet |
| Presinaptik iz | Son presinaptik olayların zamansal izi | Baglanti | Kısa | Hayır |
| Postsinaptik iz | Hedef dendritte/nöronda postsinaptik yanıtın izi | Hedef tarafındaki yerel mekanizma; bağlantıya ait kayıt | Kısa | Hayır |
| Uygunluk izi | Yakın geçmişteki pre/post etkinliğin gecikmiş modülatöre açık etiketi | Baglanti | Orta | Hayır |
| Kullanım izi | Bağlantının yakın ve uzun dönem kullanım geçmişi | Baglanti | Orta/uzun | Geçici, sürekli yenilenir |
| Yapısal bütünlük | Bağlantının fiziksel/işlevsel varlığını temsil eden durum | Baglanti ve yerel bakım kuralı | Uzun | Evet, bağlantı ömrü boyunca |
| Nöron etkinlik ortalaması | Nöronun uzun dönem ateşlenme/aktivite seviyesi | Noron | Uzun | Durum değişkeni |
| Kimyasal kaynak | Salınan sinyalin uzay-zamandaki kaydı | KimyasalAlan | Sinyale göre | Geçici |

**Kural:** Bir parametrenin yalnızca adı “potansiyel”, “iz” veya “etki” diye öğrenme ağırlığı olduğu varsayılmaz. Her parametre tek bir işlev ve zaman ölçeğine sahip olmalıdır.

## 4. Önerilen veri sözleşmesi

Gerçek yönlü bağlantı `Baglanti`, aşağıdaki kavramların sahibidir:

1. İletim etkisi / kalıcı sinaptik etkinlik katsayısı.
2. Presinaptik olay izi.
3. Postsinaptik olayın bağlantıyla eşleştirilmiş izi veya zaman kaydı.
4. Sinaptik uygunluk izi.
5. Kullanım izi.
6. Yerel kimyasal reseptör/duyarlılık profili.
7. Yapısal bütünlük ve bakım durumu.
8. Yaşam döngüsü ve geçersizleşen olay sürümü.

Hedef dendrit, kendisine gelen gerçek sinaptik girdiyi alır ve yerel yanıtını üretir. Hedef nöronun ateşlenmesi veya dendritik yanıtı, kaynak bağlantıların uygunluk izlerini güncelleyecek yerel olay bilgisi sağlar. Bu işlemde Beyin hangi sinapsın öğrenmesi gerektiğini seçmez; yalnızca olayın ilgili hedefe ulaşmasını sağlar.

Dendrit-terminal iç-yönlendirme eşlemesi korunur; fakat ayrı adlandırılır ve ayrı test edilir. İleride bu parametre, gerçek sinaptik etkinlik katsayısına sessizce bağlanmaz.

## 5. Öğrenme güncellemesinin tek sahipli olması

Her kalıcı parametre için tek bir güncelleme otoritesi vardır:

- Gerçek sinaptik etkinlik katsayısını bağlantının yerel plastisite kuralı günceller.
- Dendrit-terminal katkısını ilgili dendritin yerel kuralı günceller.
- Nöron homeostazı nöronun kendi uzun dönem etkinlik durumunu günceller.
- Yapısal bakım ve kopma kararı bağlantının yerel bakım kuralında verilir.
- Beyin yalnızca zaman ve olay dağıtımı yapar.

Aynı deneyim hem dendrit katkısını hem sinaptik ağırlığı değiştirebilir; ancak bu iki değişiklik farklı mekanizmalar ve ayrı ölçümler olarak raporlanır. Aynı parametre iki kez güncellenemez.

## 6. Üç faktörlü öğrenme için zorunlu ayrıntı

Uygunluk izi ile kalıcı ağırlık farklıdır. Uygunluk izi, pre/post etkinlikten doğan ve zamanla azalan geçici bir etikettir. Modülatör sinyal geldiğinde bağlantı:

- sinyalin kendi konumundaki yoğunluğunu,
- reseptör duyarlılığını,
- mevcut uygunluk izinin işaretini ve büyüklüğünü,
- sinyalin geldiği zamanı,
- daha önce aynı uygunluk izinin ne kadarının kullanıldığını

yerel olarak değerlendirir.

Modülatör etkisi tek bir anlık yoğunluk örneğiyle sınırsızca tekrar uygulanmamalıdır. Güncelleme, modülatör maruziyeti boyunca uygunluk izi ile ağırlıklandırılmış zaman integrali veya eşdeğer, tek-kullanımlı olay güncellemesi olarak tanımlanmalıdır. Böylece aynı kimyasal kaynak her sorguda ağırlığı tekrar tekrar değiştirmez.

## 7. Mevcut koddan çıkan temel sorunlar ve kararlar

### Sorun A — Geçici terminal potansiyeli ile kalıcı sinaptik etkinlik karışabilir

**Karar:** İki ayrı değişken olacak. Terminal hazır olma potansiyeli eşik/aktivasyon seçimi için geçici kalacak. Gerçek sinaptik etkinlik katsayısı hedef dendrite iletilen etkiyi çarpacak ve plastisiteyle değişecek.

### Sorun B — Mevcut dendrit katkısı biyolojik sinaptik ağırlık gibi okunabilir

**Karar:** Dendrit katkısı iç-yönlendirme parametresi olarak kalacak. Gerçek sinaptik ağırlık olarak adlandırılmayacak ve testlerde ayrı raporlanacak.

### Sorun C — Postsinaptik etkinlik bağlantıya geri eşlenmiyor

**Karar:** Hedef dendrite ulaşan sinaptik olayın kaynak bağlantı kimliği korunacak. Hedef taraftaki postsinaptik yanıt, yalnızca gerçekten bu dendritik olaya katılan bağlantılar için uygunluk izi oluşturabilecek. Sadece aynı nöronun ateşlenmiş olması, bütün gelen sinapsları otomatik olarak eşit biçimde uygun saymak için yeterli değildir; yerel dendrit yanıtı ve olay ilişkisi korunmalıdır.

### Sorun D — STDP tek başına davranışsal öğrenme için yeterli değil

**Karar:** STDP benzeri zamanlama kuralı, kısa zaman ölçekli yerel sıralama bileşeni olacak. Saniyeler veya daha uzun gecikmeli sonuçlar için uygunluk izi + üçüncü faktör katmanı kullanılacak. Tek başına STDP ile genel görev öğrenmesi iddia edilmeyecek.

### Sorun E — Mevcut kimyasal alan her kaynak için bütün geçmişi tarıyor

**Karar:** Önce matematiksel alan modeli ve birim/sınır koşulları netleştirilecek. Sonra ölçümle gerekirse uzamsal/zamansal indeksleme yapılacak. Etki yarıçapı performans uğruna keyfî kesilmeyecek.

### Sorun F — Mevcut bakım tasarımı bu sprint dalında henüz bulunmuyor

**Karar:** Entegrasyondan bağımsız bakım olayları, ileriki yapısal plastisite adımında eklenecek. Bakım değerlendirmesinin zamanı yerel bağlantı kuralınca seçilecek; Beyin yalnızca planlayacak. Geçen zaman tek başına kopma nedeni olmayacak.

## 8. Aşama 1 kabul ölçütleri

Teorik kabul:
- Geçici terminal potansiyeli ile kalıcı sinaptik etkinlik birbirinden ayrıldı.
- Dendrit-terminal katkısı ile gerçek pre→post bağlantı öğrenmesi ayrıldı.
- Her öğrenme değişkeninin sahibi ve zaman ölçeği tanımlandı.
- Uygunluk izinin modülatörle nasıl etkileşeceği ve tekrar uygulama sorunu tanımlandı.
- Beyin'in öğrenme kararı vermediği korundu.

Uygulama kabulü henüz sağlanmadı:
- Kodda değişkenler henüz ayrılmadı.
- Bu sözleşmeye ait yeni testler henüz eklenmedi.
- Test paketi bu denetimden sonra bu ortamda çalıştırılmadı.

## 9. Bir sonraki aşamaya geçiş

Aşama 2, ölçüm ve deney altyapısıdır. Deneyler en baştan şu ayrı serileri kaydetmelidir:

- geçici terminal potansiyeli,
- kalıcı sinaptik etkinlik katsayısı,
- dendrit-terminal katkısı,
- pre/post zaman izleri,
- uygunluk izi,
- modülatör yoğunluğu ve maruziyet,
- nöron ateşlenme oranı,
- bağlantı yapısal durumu.

Ölçüm sistemi öğrenme kararlarını vermez; yalnızca deney durumunu gözlemler. Aynı seed ve aynı başlangıç koşullarında aynı olay sırası ve aynı sonuçların üretilmesi beklenir.
