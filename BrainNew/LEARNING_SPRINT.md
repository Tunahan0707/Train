# BrainNew — Birleşik Öğrenme Sprinti (v2)

**Durum:** Uygulama sürüyor. Eğitim temeli ve dallanan geriye feedback'in ilk prototipi eklendi; kabul testleri henüz yerel ortamda çalıştırılmadı.  
**Hedef dal:** `fix/brainnew-architecture-audit`  
**Planın amacı:** BrainNew'i yerel biyolojik-esinli mekanizmalarla deneyimden kalıcı ilişki öğrenebilen, öğrendiğini geri çağırabilen ve sonunda matematiksel görevlerde genelleme gösterebilmesi sınanabilen bir simülasyona dönüştürmek.

Bu belge, önceki sprint taslağını güncel kod, proje hedefi ve kullanıcının açık tasarım kararlarıyla yeniden birleştirir. Önceki adımların tarihsel notları yerine geçer; aşağıdaki uygulama sırası ve kabul kapıları esas alınmalıdır.

---

# 0. Tasarım otoritesi ve karar hiyerarşisi

Belgeler ve önceki öneriler arasında çelişki var. Uygulama sırasında aşağıdaki öncelik kullanılacaktır:

1. **Kullanıcının açık kararları:** `Fikir Değerlendirme (22).txt` içindeki mimari kararlar bağlayıcıdır.
2. **Projenin amacı ve üçüncü tasarım sıfırlaması:** `Fikir Değerlendirme (23).txt` içindeki hedef ve yöntem korunur. Eski kod veya eski branch, yeni tasarımın otomatik doğrusu sayılmaz.
3. **Sonraki açık uygulama yetkisi:** Kullanıcı, mevcut depo ve önceki tasarım bağlamı incelenerek eksik kararların araştırılmasına, makul biçimde tamamlanmasına ve uygulama yapılmasına izin vermiştir.
4. **Aktif branch kodu:** Mevcut prototiptir; tasarım sözleşmesiyle çelişen davranışlar gerektiğinde düzeltilecektir.
5. **Asistanın eski önerileri:** `Fikir Değerlendirme (27).txt` ve eski tasarım belgeleri ancak açık kullanıcı kararlarıyla çelişmedikleri ölçüde referanstır. Kullanıcı kararı yerine geçmez.

Özellikle:

- Mikroglia **bağımsız ajanlar** olacaktır. Bağlantı nesnesinin içine gömülmüş mikroglia yaklaşımı kabul edilmeyecektir.
- Beyin yalnızca orkestratördür. Öğrenme, bağlantı seçimi, geri bildirimin yorumu ve yapısal değişim kararı merkezi Beyin tarafından verilmeyecektir.
- Pozitif geri bildirim, etkin sinapsların aktivasyon eşiğini düşürür ve etkin olmayanların eşiğini yükseltir. Negatif geri bildirim bunun tersini yapar. Bu karar, eski tasarım metinlerindeki yalnızca potansiyel değiştiren feedback önerisinden önceliklidir.
- Dendrit-sinaps katkısı, sinapsın yerel potansiyeli, sinapsın aktivasyon eşiği, gerçek sinaptik iletim etkinliği ve nöron membran eşiği ayrı değişkenlerdir.
- Sinaps-sinaps ilişkileri başlangıçta sıfırdır; yönlüdür ve iki yön bağımsız öğrenilir.
- Kullanılmama tek başına fiziksel kopma nedeni değildir.
- Elektriksel ve kimyasal sinyaller ayrı tutulur.
- 2B uzamsal temsil, yerel etkileşim, seyrek veri yapıları, deterministik olay sırası ve sınırlı parametre değişimleri korunur.
- Gerçek biyoloji ile hesaplamalı soyutlama birbirine karıştırılmaz. Her denklem için bunun biyolojik bulgu mu, model varsayımı mı, yoksa performans tercihi mi olduğu belirtilir.

## 0.1. Projenin amacı

BrainNew'in amacı hazır bir öğrenme algoritmasını nöronların üzerine yerleştirmek değildir. Amaç; elektriksel iletim, dendritik bütünleşme, yerel plastisite, kimyasal modülasyon, mikroglia benzeri yapısal bakım ve yerel geri bildirim gibi görece basit mekanizmaların etkileşiminden öğrenme, hafıza ve karar verme davranışlarının ortaya çıkıp çıkamayacağını araştırmaktır.

Matematik öğrenebilmesi nihai uygulama hedeflerinden biridir. Ancak matematiksel işlem yapan bir algoritma doğrudan nöronların içine kodlanmayacaktır. Sayılar ağa temsil olarak sunulacak; görev ortamı doğru cevabı değerlendirecek; ağın davranışı kendi yerel mekanizmalarıyla değişecektir.

## 0.2. Kapsam dışı

Bu sprintte şunlar yapılmayacaktır:

- Geri yayılım (backpropagation), gradyan inişi, hazır yapay sinir ağı öğrenme algoritmaları veya merkezi kayıp minimizasyonu.
- Nöronların içine toplama, çıkarma veya başka matematiksel işlemleri doğrudan kodlamak.
- Bilinç, dil anlama veya insan beyninin eksiksiz simülasyonu iddiası.
- İyon kanallarının, protein sentezinin veya mikroglia morfolojisinin moleküler ölçekte simülasyonu.
- Baştan büyük bir beyin ölçeğine ulaşmaya çalışmak.
- Ölçülmemiş darboğazlar için erken optimizasyon.

---

# 1. Aktif branch'in gerçek durumu

Aşağıdaki envanter tarihsel başlangıç incelemesidir; aktif dalın güncel durumu için `IMPLEMENTATION_PROGRESS.md` ve kod esas alınmalıdır. Testler çalıştırılmadan davranış kabul edilmiş sayılmaz.

## 1.1. Kodda bulunan temel parçalar

| Parça | Mevcut durum | Sprint açısından anlamı |
|---|---|---|
| `Beyin.py` | Olay kuyruğu, simülasyon saati, nöron ve bağlantı uzamsal indeksleri, mikroglia bakım olayları | Orkestrasyon çekirdeği var |
| `Noron.py` | Membran entegrasyonu, aksiyon potansiyeli fazları, seçici çıkış sinapsı aktivasyonu, yerel öğrenme çağrıları, homeostatik eşik | Temel nöral döngü var |
| `Dendrid.py` | İşaretli girdi toplama, kimyasal reseptör yanıtı, dendrit-terminal katkıları ve katkı öğrenmesi | Nöron-içi yönlendirme soyutlaması var |
| `Baglanti.py` | Yerel terminal potansiyeli/eşiği, iletim gecikmesi, transmitter profili, kalıcı sinaptik katsayı, pre/post izleri, STDP, uygunluk izi, modülatör güncellemesi, yapısal durum | Birçok öğrenme değişkeni var; kuralların tek sözleşmede birleştirilmesi gerekiyor |
| `KimyasalAlan.py` | 2B analitik kaynak-tabanlı yayılım ve temizlenme | Kimyasal alanın ilk sürümü var |
| `Mikroglia.py` | Bağımsız 2B ajan, yerel bağlantı taraması, stabilizasyon/budama ve kopma | Kullanıcı kararına uygun bağımsız mikroglia var |
| `UzamsalIndeks.py` | Hücre tabanlı 2B yerel aday arama | Seyrek uzamsal arama var |
| `DeneyKaydi.py` | Pasif olay kaydı | Gözlem altyapısı var |
| `DeneySurucusu.py` | Her örnek için yeni Beyin oluşturan baseline ölçümü | Eğitim yürütücüsü değil |
| `ReseptorOrgan.py`, `MotorOrgan.py` | Boş dosyalar | Girdi/çıktı arayüzleri henüz yok |

## 1.2. Kodda bulunan öğrenme ve plastisite

- Dendritin kendi nöronunun çıkış terminallerine yerel katkısı öğrenilebiliyor.
- Gerçek pre→post bağlantı için ayrı `sinaptik_agirlik` değişkeni var.
- Bağlantı bazında presinaptik ve postsinaptik izler var.
- Pre→post sıralaması LTP, post→pre sıralaması LTD yönünde değişim oluşturabiliyor.
- İşaretli ve sönümlü uygunluk izi var.
- `odul - ceza` kimyasal alanı uygunluk izini kalıcı ağırlık değişimine dönüştürebiliyor.
- Nöron kendi ateşlenme etkinliğini izleyip ateşlenme eşiğini homeostatik olarak ayarlıyor.
- Mikroglia bağımsız ajan olarak bağlantı yapısal durumunu değerlendirebiliyor.
- Yerel kimyasal büyüme sinyali ve dendrit reseptör uygunluğuyla kontrollü yeni bağlantı kurulabiliyor.

Bunlar mekanizma altyapılarıdır. Aynı ağın görev deneyimiyle öğrenip öğrenmediğini, örüntüyü geri çağırıp çağırmadığını veya genelleme yapıp yapmadığını henüz kanıtlamaz.

## 1.3. Henüz bulunmayan ana yetenekler

- Kalıcı eğitim döngüsünün görev geri bildirimiyle tam entegrasyonu ve episode iz politikası.
- Görev ortamı ve ödül/ceza sinyalinin ağdan bağımsız üretimi.
- Yönlü sinaps-sinaps ilişkileri ve bunların birlikte etkinleşme öğrenmesi.
- Yerel nöron-nöron birlikte etkinleşme etkileşimi.
- Dallanmış geriye feedback'in çoklu seed, gecikme, döngü ve ablation testleri.
- Yeni bağlantıların otomatik yerel zamanlaması ve olgunlaşma dinamiği.
- Mevcut zayıf bağlantının kademeli onarımı ve tamamen bağlantısız nöronun toparlanma durumu.
- Kısmi ipucundan örüntü tamamlama ve geri çağırma deneyleri.
- Matematiksel girdilerin/çıktıların temsili ve matematik görevleri.
- Uzun süreli öğrenme, unutma ve eski-yeni görev etkileşimi deneyleri.

## 1.4. İncelemede görülen önemli uyumsuzluklar

Bunlar sprintin ilk düzeltme kapısına alınacaktır:

1. **Eğitim yürütücüsü ile eğitim sistemi karıştırılmamalı.** Mevcut `DeneySurucusu` her örnek için yeni ağ kurar; öğrenilmiş durumu örnekler arasında taşımaz.
2. **Feedback sözleşmesi belgeler arasında çelişiyor.** Kullanıcının açık kararı eşiklerin etkinlik durumuna göre ters yönlerde değiştirilmesidir. Eski metindeki yalnızca potansiyel değiştiren feedback kuralı bağlayıcı değildir.
3. **STDP olay atfı açıkça belgelenmeli.** Kod, hedef nöron ateşlenmesinde gelen bağlantıların post izlerini güncelliyor. Eski denetim metni yalnızca o anki entegrasyona kaynak olan bağlantıları işaret etmeyi söylüyor. Bunlar aynı kural değildir. Sprintte bağlantı-yerel pre/post izlerinin hangi olayda ve hangi bağlantı için değişeceği tek bir kurala bağlanacak; bağlantıların nedensel geçmişi yalnızca “aynı entegrasyonda girdi var mıydı?” kontrolüne indirgenmeyecek.
4. **Modülatör örnekleme aralığı davranışı etkiliyor.** Şu an gecikmiş modülatör, kaynak nöronun entegrasyon/bakım akışında örnekleniyor. Kısa kimyasal darbeler iki örnekleme arasında kalırsa kaçabilir. Bu, görev öğrenmesinden önce çözülmeli.
5. **Budanmış bağlantının bekleyen iletim olayları geçersizleşmeli.** Bağlantı koparıldıktan sonra olay kuyruğunda daha önceden planlanmış bir sinaptik girdi kalabilir. Olay çalıştığında kopuk bağlantıdan gelen sinyalin hedefe ulaşması engellenmeli.
6. **Kimyasal nokta kaynak formülünün başlangıç davranışı sınanmalı.** Mevcut 2B impuls çekirdeği kaynak konumunda salım zamanına çok yakınken tekilleşebilir. Sonlu salım yarıçapı veya eşdeğer düzenleme gerekip gerekmediği kararlaştırılmalı.
7. **Simülasyon zaman birimi açıkça sabitlenmeli.** İletim, aksiyon potansiyeli fazları, iz sönümü, kimyasal yayılım ve bakım aralıkları aynı zaman birimiyle ifade edilmeli. Olay sıralama için kullanılan sayısal epsilon, biyolojik gecikme gibi yorumlanmamalı.
8. **İşaret değişimi desteği netleştirilmeli.** Projenin önceki hedeflerinde bağlantıların güçlenmesi, zayıflaması ve gerektiğinde işaret değiştirmesi yer alıyor. Mevcut `sinaptik_agirlik` yalnızca [0,2] aralığında; işaret `etki` değişkeninde sabit. Etkin sinaptik katsayının işaret değiştirebilmesi için parametre sahipliği ve güvenli sınırlar tanımlanmalı.
9. **Kimyasal kaynakların yaşam döngüsü sınırsız kalmamalı.** Kaynakların listede sonsuza kadar tutulması uzun deneylerde bellek maliyeti doğurabilir. Temizleme, alanın anlamını değiştirmeyen doğruluk toleransıyla ele alınmalı.
10. **Dokümantasyonun otoritesi yenilenmeli.** Eski branch'ten gelen tasarım metni yeni üçüncü tasarımın üstüne yazmamalı. Kullanıcı kararları ve güncel kod durumu ayrı ayrı belirtilmeli.

---

# 2. Sprintin tamamlanma tanımı

Sprint bittiğinde aşağıdaki iddialar ayrı ayrı deneyle gösterilebilmelidir:

1. Aynı ağ, farklı eğitim örnekleri boyunca kalıcı öğrenilmiş durumunu korur.
2. Öğrenme yalnızca geçici potansiyel artışı değildir; kalıcı ve ölçülebilir yerel parametre değişimi üretir.
3. Öğrenilmiş değişiklik, doğru/yanlış geri bildirimin zamanlamasına ve ilgili yerel izlere bağlıdır.
4. Ağ A→B ile B→A sıralamalarını ayırt edebilir.
5. Sinapslar arası yönlü ilişkiler birlikte etkinleşme ve tek taraflı etkinleşme deneyiminden öğrenilir.
6. Yerel nöron-nöron etkileşimi yalnızca uzamsal/zamansal olarak ilgili nöronları etkiler.
7. Geri bildirim dallanabilir; her dalın etkisi azalır ve yerel iz eşiği altına düşünce bağımsız olarak durur.
8. Pozitif/negatif feedback, kullanıcının tanımladığı etkin/inaktif sinaps eşik kuralını uygular.
9. Kimyasal sinyaller elektriksel iletimden ayrı çalışır; transmitter repertuvarı, salım miktarı, yayılım, temizlenme ve reseptör duyarlılığı birbirinden ayrıdır.
10. Mikroglia bağımsız ajan olarak yerel aktivite/kimyasal işaretleri değerlendirir; yalnızca kullanılmama nedeniyle bağlantı silmez.
11. Yeni bağlantı zayıf başlar; kullanım ve yerel kimyasal işaretlerle olgunlaşır. Mevcut bağlantının onarımı ile kopmuş bağlantının yeniden oluşması farklı süreçlerdir.
12. Ağın aşırı etkinleşmesi veya tamamen sessizleşmesi sınırlandırılır; homeostaz öğrenilmiş ayrımları otomatik silmez.
13. Ağ tam örüntüyü, kısmi/gürültülü ipucundan geri çağırabilir.
14. Öğrenme verisinde bulunmayan örneklerde genelleme başarısı ölçülür; ezberleme genelleme diye raporlanmaz.
15. Aynı ağ üzerinde ardışık görevler öğretildiğinde eski bilgi kaybı ölçülür.
16. En azından basit sayısal görevlerde ağın öğrenme/genelleme kapasitesi sınanır.
17. Bütün sonuçlar seed, görev, eğitim/test ayrımı, parametre yapılandırması ve mekanizma ablasyonlarıyla tekrarlanabilir.

Bir sinapsın ağırlığının değişmesi, tek başına öğrenme kanıtı değildir. Öğrenme iddiası görev performansındaki, geri çağırmadaki ve görülmemiş örneklere genellemedeki ölçülebilir değişime dayanır.

---

# 3. Birleşik sprintin uygulama aşamaları

Sprint tek bir bütün olarak yürütülecek; ancak aşağıdaki iç kapılar korunacak. Kapılar kodu parçalara bölmek için değil, hatalı bir mekanizmanın sonraki mekanizmaları kirletmesini önlemek içindir. Her aşamanın kodu, testleri ve dokümantasyonu aynı çalışma dalında tamamlanır. Yeni branch veya PR açılmaz.

## Aşama 1 — Mimari sözleşmeyi ve kod sahipliğini dondur

**Amaç:** Kullanıcı kararları, eski tasarım önerileri ve mevcut prototip arasındaki ayrımı kesinleştirmek.

Yapılacaklar:
- Her öğrenilebilir değişkenin anlamı, sahibi, güncelleme tetikleyicisi, sınırı ve zaman ölçeği listelenecek.
- Nöron membran eşiği, sinaps aktivasyon eşiği, sinapsın yerel potansiyeli, gerçek sinaptik etkinlik katsayısı, dendrit-terminal katkısı, sinaps-sinaps ilişkisi, yapısal bütünlük ve uygunluk izi ayrı tutulacak.
- Gerçek pre→post bağlantı ile nöron-içi dendrit→çıkış-terminali yönlendirme soyutlaması açıkça ayrılacak.
- Mikroglia bağımsız ajan olarak sabitlenecek.
- Beyin'in izin verilen sorumlulukları: olay kuyruğu, simülasyon saati, uzamsal aday sorgusu ve veri/olay iletimi. Beyin'in yasak sorumlulukları: öğrenme hesabı, sinaps seçimi, geri bildirim yorumu, budama ve büyüme kararı.
- Dosya ve sınıf adları Türkçe kalacak; gereksiz yeni soyutlama katmanı eklenmeyecek.

**Kabul ölçütü:** Her öğrenilebilir durumun tek bir sahibi olacak; aynı öğrenme olayı iki ayrı bileşende iki kere uygulanmayacak; kullanıcı kararı ile çelişen eski metinler açıkça tarihsel/referans olarak etiketlenecek.

## Aşama 2 — Olay kuyruğu, zaman ve nedensellik doğruluğu

**Amaç:** Öğrenme kurallarının doğru olay sırasına ve doğru zamana göre çalışmasını garanti etmek.

Yapılacaklar:
- Simülasyonun zaman birimi bütün parametre ve belgelerde aynı şekilde tanımlanacak. Milisaniye temel zaman birimi olarak kullanılacak; alt-milisaniye olaylar yalnızca açıkça tanımlanmış fiziksel gecikmelerse kullanılacak.
- Olay sıralaması: aynı zaman damgasındaki duyusal/sinaptik girdiler, entegrasyon, ateşlenme/terminal aktivasyonu, feedback ve faz geçişleri için deterministik öncelik tablosu oluşturulacak.
- Aynı hedefe aynı zamanda ulaşan feedback olayları mutlak etki büyüklüğü azalan sırayla; eşitlikte olay kimliğiyle işlenecek.
- Gecikmeli iletim olayları kaynak bağlantı kimliğini koruyacak.
- Bağlantı kopunca önceden kuyruğa konmuş iletim olayları geçersiz sayılacak; kopuk bağlantıdan hedefe yeni etki uygulanmayacak.
- Aynı entegrasyon için olay tekilleştirme korunacak.
- Mevcut model kararı: refrakter dönemde gelen girdi dendritte tamponlanır; faz döngüsü tamamlandığında bir kez entegrasyona alınır. Bu davranış, hem olay sırası hem de tekrar oynatma/çift işleme regresyon testleriyle korunur. Daha sonra biyolojik sönüm modeli gerekirse ayrı deneyle değerlendirilir; mevcut kararı sessizce değiştirme.
- Olay limiti, sonlu zaman ufku ve otomatik mikroglia bakım döngüsü birlikte doğrulanacak.

**Kabul ölçütü:** Aynı seed ve olay dizisi aynı sırayı üretir; kopmuş bağlantıdan eski sinyal sızmaz; refrakterlik sinyali yapay biçimde geleceğe taşımaz; kaynak nöronun faz döngüsü hedef nöronun bağımsız ateşlenmesini engellemez.

## Aşama 3 — Sayısal güvenlik ve kimyasal alanın kararlılaştırılması

**Amaç:** Parametrelerin sınırlarını ve kimyasal alanın zaman davranışını güvenilir kılmak.

Yapılacaklar:
- Bütün parametreler sonlu değer, alt/üst sınır ve geçerli zaman kontrolünden geçecek.
- Yerel potansiyel [-1,+1] sınırında kalacak.
- Sinaps aktivasyon eşiği, nöron membran eşiği ve öğrenilmiş sinaptik katsayı birbirine karıştırılmayacak.
- Sinaptik etkinlik katsayısının işaret değiştirmesi için ayrı işaretli katsayı veya işaretli ağırlık temsili seçilecek. Başlangıçta uyarıcı/baskılayıcı işaret korunacak; öğrenme kuralı işareti ancak tanımlı sınır ve yerel koşullarda değiştirebilecek.
- Kimyasal alanın impuls çözümü sonlu salım hacmi/yarıçapıyla düzenlenecek veya aynı matematiksel davranışı koruyan başka sonlu kaynak profili kullanılacak. Kaynak konumunda salım anına yakın sayısal tekillik kabul edilmeyecek.
- Her kimyasal tür için ayrı yayılım, temizlenme ve reseptör yanıtı parametreleri bulunacak.
- Kimyasal kaynakların bellekte tutulma süresi ve güvenli temizleme eşiği tanımlanacak; temizleme toleransı davranış karşılaştırmasıyla ölçülecek.
- Kimyasal yoğunluk ve reseptör yanıtının aşırı büyümesi/taşması kontrol edilecek.

**Kabul ölçütü:** Kaynak noktasında sonsuz/NaN yoğunluk oluşmaz; aynı kaynaklar için alan değeri zamanla doğru yönde değişir; farklı transmitter türleri birbirinin parametrelerini kullanmaz; kaynak temizliği seçilen toleransın dışında ölçülebilir sinyal kaybı oluşturmaz.

## Aşama 4 — Tekrarlanabilir ağ kurucu ve başlangıç topolojisi

**Amaç:** Elle bağlanmış iki nöron demosundan gerçek bir seyrek ağa geçmek.

Yapılacaklar:
- Seed alan tek bir ağ kurucu oluşturulacak.
- Nöron konumları 2B uzayda üretilecek.
- Dendrit sayısı, çıkış terminali sayısı, bağlantı olasılığı, bağlantı yarıçapı ve başlangıç parametreleri konfigürasyonla belirlenecek.
- Önceki tasarım konuşmalarında geçen yaklaşık 6–12 dendrit ve 5–10 çıkış terminali aralıkları ilk deneme aralıkları olarak değerlendirilecek; biyolojik sabit veya zorunlu sayı sayılmayacak.
- Başlangıç ağı seyrek olacak; bütün nöronlar birbirine bağlanmayacak.
- Bağlantıların işaretleri/etki yönleri pozitif ve negatif örnekler içerecek.
- Bağlantı uzunluğu ve iletim hızı gecikmeyi belirleyecek.
- Aynı seed aynı nöron, dendrit, terminal, bağlantı kimliği ve başlangıç parametrelerini üretmeli.
- Ağ kurucu öğrenme kuralı uygulamayacak; yalnızca başlangıç yapısını oluşturacak.
- Ağın yoğunluğu, izole nöron oranı, giriş/çıkış erişilebilirliği ve bağlantı uzunluğu dağılımı raporlanacak.

**Kabul ölçütü:** Aynı konfigürasyon ve seed aynı topolojiyi üretir; bağlantılar seyrek ve uzamsal olarak sınırlıdır; başlangıçta erişilemeyen hedefler ve tamamen bağlantısız düğümler ölçülür; ağ kurucu öğrenme davranışını gizlice kodlamaz.

## Aşama 5 — Reseptör ve motor organı: görev arayüzü

**Amaç:** Simülasyonun dış dünyadan girdi alması ve kendi çıktısını ölçülebilir biçimde sunması.

Yapılacaklar:
- `ReseptorOrgan` dış girdiyi nöral ağa dönüştüren tek arayüz olacak.
- `MotorOrgan` ağın ateşlenme/aktivite örüntüsünü dış çıktıya dönüştürecek.
- Organlar öğrenme ağırlıklarını değiştirmeyecek.
- Reseptör organı sayı, sembol veya örüntü için önceden belirlenmiş kodlama kullanabilir; ancak kodlama işleminin kendisi matematiksel cevabı hesaplamayacak.
- Motor organı çıktı nöronlarının etkinlik örüntüsünü okuyacak; görev cevabını seçme/çözme işlemi dış arayüzde kalacak.
- Girdi ve çıktı kanalları birbirinden ayrılacak; aynı örnek hem girdi hem beklenen çıktı olarak ağa sızmayacak.

**Kabul ölçütü:** Ağın içine doğrudan beklenen cevap veya hazır çözüm yazılmadan girdi sunulabilir ve çıktı okunabilir. Organlar kapatıldığında nöronların yerel öğrenme kuralları değişmez.

## Aşama 6 — Kalıcı öğrenme oturumu ve episode yaşam döngüsü

**Amaç:** Aynı ağın deneyimden öğrenmesini mümkün kılmak.

Yapılacaklar:
- Mevcut baseline `DeneySurucusu` korunacak; görevi yeni ağlarla başlangıç performansını ölçmek.
- Ayrı bir eğitim yürütücüsü oluşturulacak. Aynı `Beyin` nesnesi eğitim örnekleri boyunca korunacak.
- Episode başında yalnızca geçici durumlar tanımlı kurala göre temizlenecek/sönümlenecek: bekleyen duyusal girdiler, kısa ömürlü potansiyeller, olay kuyruğu, episode'a ait geçici ölçümler.
- Kalıcı öğrenilmiş durumlar korunacak: sinaptik katsayılar, dendrit katkıları, öğrenilmiş sinaps ilişkileri, öğrenilmiş nöron etkileşimleri ve bağlantı yapısı.
- Uygunluk izleri ve kısa ömürlü etkinlik izleri zorla sıfırlanmak yerine tanımlı sönüm/episode politikasıyla yönetilecek. Deneyler arası iz sızıntısı ayrıca ölçülecek.
- Eğitim, doğrulama ve test verileri kimlik ve içerik bakımından ayrılacak.
- Test örnekleri hiçbir zaman eğitim sırasında ağa veya kimyasal alana sunulmayacak.
- Eğitim sırası seed ile belirlenebilir olacak.
- Deney kaydı parametre anlık görüntüsü, seed, görev, episode, olay sayısı ve sonuçları tutacak.

**Kabul ölçütü:** Aynı ağ birinci örnekten sonra ikinci örnekte önceki öğrenilmiş değişiklikleri korur; episode temizliği kalıcı öğrenmeyi silmez; yeni ağ kurmadan eğitim devam eder; test verisi eğitim döngüsüne ulaşmaz.

## Aşama 7 — Öğrenme öncesi baseline görevleri

**Amaç:** Öğrenme eklenmeden ağın ne yapabildiğini bilmek.

İlk görev ailesi:
- B1: Tek örüntü/girdi-çıktı eşlemesi.
- B2: İki örüntüyü ayırt etme.
- B3: A→B ve B→A zamansal sıra ayrımı.
- B4: Gürültülü girdiye dayanıklılık.
- B5: Kısmi girdiden örüntü tamamlama.
- B6: Eğitimde görülmeyen örneklerde genelleme.

Yapılacaklar:
- Her görev için eğitim, doğrulama ve test kümeleri oluşturulacak.
- Başlangıç ağının başarı oranı ve yanlış pozitif/negatifleri ölçülecek.
- Rastgele/başlangıç ağının sonuçları saklanacak; sonraki öğrenme kazanımları bu baseline'a göre raporlanacak.
- Tam eşleşme yanında sınıf bazlı doğruluk ve çıktı etkinliği raporlanacak.

**Kabul ölçütü:** Öğrenme kapalı ağın davranışı ölçülmüş ve tekrar üretilebilir olmalı. Başlangıç ağının başarısız olması hata değildir; karşılaştırma noktasıdır.

## Aşama 8 — Yerel sinaptik plastisiteyi tek kurala bağla

**Amaç:** Mevcut Hebbian, STDP ve uygunluk izi kodunu birbirine karıştırmadan tanımlamak.

Yapılacaklar:
- Her bağlantı kendi pre/post izlerini ve uygunluk izini tutmaya devam edecek.
- İzlerin geçici, sinaptik etkinlik katsayısının kalıcı olduğu ayrımı korunacak.
- Pre→post ve post→pre sıralamasının işaretli değişimleri test edilecek.
- STDP penceresi ve zaman sabitleri simülasyon zaman birimiyle tutarlı hâle getirilecek.
- Kullanılmayan bağlantı yalnızca başka bağlantı aktif olduğu için cezalandırılmayacak.
- LTP/LTD sınır doygunluğu ve işaret değişimi matematiksel olarak güvenli olacak.
- Aynı pre/post olayının iki kez işlenmesi engellenecek.
- Hebbian/STDP güncellemesi ile gecikmiş modülatör güncellemesinin aynı olayı istemeden iki kez ödüllendirmesi önlenecek. İki mekanizma ayrı deney anahtarlarıyla açılıp kapatılabilecek.
- Sinaptik ağırlık, dendrit-terminal katkısı ve terminalin geçici aktivasyon potansiyeli ayrı tutulacak.

**Kabul ölçütü:** Pre→post ve post→pre sıraları farklı sonuç verir; zaman penceresi dışındaki olay değişim oluşturmaz; ilgisiz bağlantılar değişmez; katsayı sınırları korunur; her mekanizmanın katkısı tek başına ölçülebilir.

## Aşama 9 — Gecikmiş modülatör ve uygunluk izi

**Amaç:** Yakın geçmişte etkin olmuş bağlantıların daha sonra gelen kimyasal geri bildirimle seçici biçimde değişebilmesi.

Yapılacaklar:
- Uygunluk izi yerel pre/post etkinlikten oluşacak ve kendi zaman sabitiyle sönecek.
- Ödül ve ceza kimyasal sinyalleri ayrı türler olarak kalacak; işaret `ödül - ceza` farkından gelecek.
- Kimyasal modülatör yalnızca bulunduğu uzamsal/zamansal etki alanındaki sinapslarca algılanacak.
- Örnekleme sıklığı nöronun tesadüfi entegrasyon sayısına bağlı kalmayacak. Kısa darbelerin kaçırılmaması için olay tabanlı, analitik integral veya doğruluğu ölçülmüş sınırlı örnekleme yöntemi seçilecek.
- Modülatörün uygunluk izini ağırlığa dönüştürmesi yalnızca bağlantı-yerel mekanizma içinde gerçekleşecek.
- Pozitif ve negatif modülatör, pozitif ve negatif uygunluk izi için dört işaret kombinasyonuyla sınanacak.
- Modülatör geldiğinde iz sönmüşse anlamlı kalıcı değişim oluşmayacak.
- Gecikme arttıkça uygunluk izinin sönümü nedeniyle etki beklenen biçimde azalacak.

**Kabul ölçütü:** Aynı ödül sinyali uygunluk izi olan ve olmayan bağlantılarda farklı sonuç üretir; kısa sinyal darbeleri tanımlı zaman çözünürlüğünde kaybolmaz; Beyin hangi bağlantının öğrenmesi gerektiğini bilmez.

## Aşama 10 — Kullanıcının feedback kuralı ve dallanan geriye yayılım

**Uygulama durumu:** İlk olay tabanlı prototip eklendi. Nöron son ateşlenmesinin gerçek nedensel girdilerini ve aktif çıkış sinapslarını saklıyor; feedback dalı bu girdiler üzerinden ters yönde ilerliyor. Her dal presinaptik iz, sönüm katsayısı ve kendi ziyaret kümesiyle bağımsız ilerliyor. Beyin yalnızca olayları zamanlıyor. Çoklu seed, gecikme, döngü ve görev başarısı testleri henüz tamamlanmadı.

**Amaç:** Geri bildirimin yalnızca doğru yerel nedensel yolları etkilemesi.

Kullanıcı tarafından belirlenen temel kural:
- Pozitif feedback, feedback dalı üzerinde etkin olmuş sinapsların aktivasyon eşiğini düşürür; etkin olmayan sinapsların eşiğini yükseltir.
- Negatif feedback bunun tersini yapar.
- Eşik değişimi sınırlıdır; sınıra yaklaştıkça güncelleme küçülür.
- Sinaps eşiği nöron membran eşiği ve sinapsın yerel potansiyelinden ayrıdır.

Dallanma:
- Feedback, son etkinlik izleri ve mevcut bağlantı yapısı üzerinden geriye doğru yayılır.
- Her dal kendi etkisini ve izini taşır.
- Her geri adımda etki azalır.
- Dal, kendi yerel etkinlik izi ilgili eşiğin altına düştüğünde durur; bir dalın durması diğer dalları durdurmaz.
- Sabit derinlik, ana durdurma kuralı olmayacak.
- Döngüsel bağlantıların sonsuz feedback üretmemesi için feedback kimliği, dal kimliği, ziyaret edilmiş bağlantılar ve iz eşiği birlikte kullanılacak.
- Aynı hedefe aynı zamanda ulaşan etkiler ayrı uygulanır; büyük mutlak etki önce, eşitlikte kararlı olay sırası.
- Beyin yalnızca feedback olayını sıraya koyar. Hangi sinapsın eşiğinin değişeceğini dal üzerindeki yerel sinaps/nöron mekanizması belirler.

**Kabul ölçütü:** Pozitif ve negatif feedback etkin/inaktif sinaps eşiklerini ters yönde değiştirir; yalnızca ilgili dallar etkilenir; dallar birbirinden bağımsız sonlanır; potansiyel/eşik sınırları aşılmaz; feedback ağırlık veya dendrit katkısı güncellemesiyle karıştırılmaz.

## Aşama 11 — Sinaps-sinaps yerel etkileşimi

**Uygulama durumu:** İlk yerel sürüm eklendi. Her nöron seyrek ve yönlü terminal ilişkileri saklıyor; birlikte etkinleşme ilişkiyi pozitif, tek taraflı etkinleşme yalnızca etkin terminalden diğerine giden yönü negatif güncelliyor. İlişki, diğer terminalin geçici potansiyelini etkiliyor ve kullanılmadığında tembel üstel sönümle zayıflıyor. Kopan terminalin ilişkileri temizleniyor. Birim testleri yazıldı; henüz çalıştırılmadı.

**Amaç:** Aynı nörona ait sinapsların birlikte etkinleşme geçmişinden yönlü ilişkiler öğrenmesi.

Kurallar:
- Her nöron yalnızca kendi sinapsları arasındaki ilişkileri tutar.
- İlişkiler seyrek ve yönlüdür: `k→j` ile `j→k` bağımsızdır.
- Başlangıçta ilişki yoktur; sıfır etki kabul edilir.
- İki sinaps birlikte etkinleşirse ilgili yönlü ilişki küçük pozitif yönde öğrenilir.
- Yalnızca biri etkin, diğeri değerlendirmeye uygun olduğu hâlde etkin değilse ilgili yönlü ilişki negatif yönde güncellenebilir.
- İkisi de etkin değilse ilişki güncellemesi yapılmaz.
- Bir sinaps aktive olduğunda mevcut `k→j` ilişkisi, diğer sinapsın geçici potansiyelini etkileyebilir.
- Öğrenilmiş ilişki katsayısı ile o anki potansiyel etkisi ayrı tutulur.
- İlişki kullanılmadıkça zamanla zayıflayabilir.
- Tüm sinaps çiftleri her zaman adımında taranmaz; yalnızca o olayda değerlendirilen yerel adaylar işlenir.

**Kabul ölçütü:** Birlikte etkinleşen çiftin ilişkisi artar; tek taraflı etkinleşme yalnızca tanımlı yönü etkiler; iki taraf da etkin değilken değişim olmaz; yönler bağımsızdır; ilişki seyrek tutulur; ilişki potansiyeli geçici, ilişki ağırlığı kalıcıdır.

## Aşama 12 — Yerel nöron-nöron birlikte etkinleşme

**Uygulama durumu:** İlk yerel sürüm eklendi. Beyin yalnızca 2B uzamsal indeksten yakın adayları buluyor; ateşlenen nöronun yerel mekanizması, zaman penceresinde yakın zamanda ateşlenmiş komşularla yönlü ilişki kuruyor. Sıralı etkinleşme önceki→sonraki yönünü, aynı zaman damgasındaki eşzamanlı etkinleşme iki yönü de güçlendiriyor. İlişki, bağlantı büyüme uygunluğunu sınırlı ölçüde etkiliyor; doğrudan spike üretmiyor. Birim testleri yazıldı; henüz çalıştırılmadı.

**Amaç:** Uzamsal olarak yakın ve zaman bakımından ilişkili nöronların birbirlerinin yerel etkilenmesini değiştirmesini modellemek.

Önceki konuşmalarda bu mekanizmanın varlığı istenmiştir; fakat hangi değişkeni değiştireceğine dair kesin formül doğrulanamamıştır. Bu nedenle en basit yerel model kullanılacaktır:

- Aday nöronlar yalnızca 2B uzamsal indeks üzerinden bulunur.
- Bir nöron ateşlendiğinde yakındaki nöronlar için kısa süreli coaktivasyon izi bırakılır.
- İkinci nöron tanımlı zaman penceresinde ateşlenirse yönlü yerel ilişki güçlenebilir.
- Tek taraflı ateşlenmede ilişki zayıflatma, yalnızca adaylık/iz koşulları karşılanırsa uygulanır; tüm yakın sessiz nöronlar cezalandırılmaz.
- İlişki doğrudan uzak nörona zorunlu spike göndermez. İlk sürümde yalnızca yerel uyarılabilirlik/etkilenme veya bağlantı oluşumu uygunluğunu küçük ölçüde modüle eder.
- İlişki başlangıçta sıfırdır, seyrek saklanır, sınırlandırılır ve kullanılmadığında zayıflar.
- Bu mekanizma gerçek sinaptik bağlantının yerine geçmez; bağlantı oluşumu ve sinaptik iletim ayrı kalır.

**Kabul ölçütü:** Yakın ve zaman penceresinde birlikte etkinleşen nöron çiftleri ilişki öğrenir; uzak veya zamansal olarak ilgisiz nöronlar etkilenmez; tüm-çift matris oluşmaz; etkinlik tek başına zorunlu doğrudan iletim yaratmaz.

## Aşama 13 — Kimyasal sinyal repertuvarı ve transmitter etkileşimi

**Amaç:** Elektriksel iletimden ayrı kimyasal sinyallerin yerel ve tür-bağımlı etkisini tamamlamak.

İlk işlevsel sınıflar:
1. Hızlı sinaptik iletim sinyalleri.
2. Dendrit ve terminal yanıtını değiştiren modülatör sinyaller.
3. Büyüme ve stabilizasyon sinyalleri.
4. Budama/hasar ve koruyucu işaretler.

Kurallar:
- Bir terminal yalnızca kendi repertuvarında bulunan transmitter türlerini salgılayabilir.
- Aynı terminal bir olayda birden fazla tür salgılayabilir; türlerin miktarları bağımsızdır.
- Her terminalin her olayda tüm repertuvarı salması zorunlu değildir.
- Dendrit reseptör duyarlılıkları tür bazında pozitif, negatif veya sıfır olabilir.
- Aynı kimyasal tür farklı dendritlerde farklı sonuç verebilir.
- Presinaptik salım düzenlemesi ile postsinaptik reseptör yanıtı ayrı parametrelerdir.
- `Q_k(x,t)` kimyasal yoğunluğu, `R_{ik}` dendrit duyarlılığı kavramsal ayrımı korunur.
- Kimyasal alanın yayılım/temizlenme parametreleri türe özeldir.
- Büyüme, stabilizasyon, budama ve koruma sinyalleri klasik nörotransmitter diye adlandırılmayacak; gerektiğinde nöromodülatör/nörotrofik/immün işaret soyutlaması olarak sınıflandırılacak.
- İlk sürümde gerçek molekül listesini gereksiz büyütmek yerine işlevsel sınıflar kullanılacak. Somut moleküller ancak model davranışına anlamlı katkı sağlıyorsa eklenecek.

**Kabul ölçütü:** Bir terminalin repertuvarı dışındaki türü üretmesi engellenir; farklı türlerin alanları karışmaz; aynı türün farklı reseptör profillerinde farklı işaretli yanıtlar üretmesi mümkündür; kimyasal alan elektriksel potansiyeli doğrudan değiştirmez, yalnızca yerel reseptör mekanizması üzerinden etkiler.

## Aşama 14 — Bağımsız mikroglia ve bağlantı yaşam döngüsünü tamamla

**Amaç:** Bağlantıların korunma, yaşlanma, zayıflama, onarım, budanma ve yeniden oluşma döngüsünü kurmak.

Mikroglia:
- Bağımsız 2B ajan olarak kalır.
- Yerel algılama yarıçapı içinde bağlantı indeksinden aday alır.
- Kullanım izi, kimyasal büyüme/stabilizasyon/budama/koruma sinyalleri ve yapısal bütünlüğü birlikte değerlendirir.
- Yalnızca kullanılmama nedeniyle bağlantıyı koparmaz.
- Beyin yalnızca bakım olayını zamanlar; mikroglia hangi bağlantıyı nasıl değiştireceğine yerel olarak karar verir.

Bağlantı yaşam döngüsü:
- İşlevsel iletim etkinliği ve yapısal bütünlük ayrı kalır.
- Zayıflamış ama fiziksel olarak mevcut bağlantı uygun kimyasal sinyallerle kademeli onarılabilir.
- Fiziksel olarak kopmuş bağlantı eski kimliğiyle diriltilmez.
- Yeni bağlantı yeni kimlik alır, zayıf başlar ve olgunlaşır.
- Olgunlaşma; kullanım izi, stabilizasyon/büyüme kimyası ve bağlantının yerel etkinliğiyle ilerler.
- Otomatik büyüme denemesi her simülasyon adımında küresel tarama yapmaz; yerel büyüme sinyali, terminal etkinliği veya bağlantısız terminalin yerel deneme zamanı gibi olaylarla tetiklenir.
- Bir nöron tek bağlantı kaybetti diye sıfırlanmaz.
- Kullanılabilir bütün çıkış bağlantılarını kaybeden nöron geçici toparlanma durumuna girebilir; büyüme duyarlılığı geçici artar, durum yeni bağlantı veya süre sınırıyla sonlanır.
- Eski bağlantının kuyruğa bırakılmış olayları kopma anında geçersizleşir.

**Kabul ölçütü:** Aktif bağlantılar rastgele silinmez; budama koşulları çok faktörlüdür; zayıf bağlantı onarılabilir; kopmuş bağlantı yeniden etkinleşmez; yeni bağlantı zayıf başlar ve olgunlaşması ölçülebilir; bağlantısız nöron sonsuz kilitlenmeye girmez.

## Aşama 15 — Homeostaz ve metaplastisite

**Amaç:** Öğrenme sırasında ağın doygunlaşmasını veya tamamen sessizleşmesini önlemek.

Yapılacaklar:
- Nöron başına uzun dönem ateşlenme etkinliği izlenir.
- Nöron ateşlenme eşiği yavaşça ayarlanır.
- Sinaptik ölçekleme, inhibitör plastisite veya metaplastisite ancak mevcut eşik homeostazının görev deneylerinde yetersiz kaldığı gösterilirse eklenir.
- Homeostaz öğrenilmiş belirli bağlantıları rastgele silmez.
- Hızlı Hebbian/STDP/feedback ile yavaş homeostatik değişim farklı zaman sabitleri kullanır.
- Aşırı etkin, düşük etkin ve dengeli ağ koşulları ayrı test edilir.

**Kabul ölçütü:** Ağın sessiz/aşırı etkin nöron oranı kontrol edilebilir; homeostaz açıkken öğrenilmiş örüntü performansı korunur; homeostaz kapalı/açık ablasyon farkı ölçülür.

## Aşama 16 — Hafıza, geri çağırma ve örüntü tamamlama

**Amaç:** Öğrenilmiş parametrelerin yalnızca sayısal olarak değiştiğini değil, davranışta kalıcı iz bıraktığını göstermek.

Yapılacaklar:
- Eğitimde sunulan örüntü, öğrenme tamamlandıktan sonra yeniden sunulacak.
- Tam örüntü yerine kısmi ipucu verilecek.
- Bazı girdiler çıkarılacak veya gürültülenecek.
- Ağın doğru çıktı örüntüsünü yeniden oluşturma oranı ölçülecek.
- Aynı ağın yeni episode'a geçmesiyle öğrenilmiş durumun korunması doğrulanacak.
- Geri çağırma için ayrı bir hazır algoritma eklenmeyecek; yerel bağlantı ve potansiyel dinamiklerinden çıkması beklenecek.
- Tamamlayamıyorsa hangi mekanizma eksik, ölçümlerden çıkarılacak; doğrudan örüntü tamamlama kodu yazılmayacak.

**Kabul ölçütü:** Ağ yalnızca eğitim girdisini aynen tekrar etmekle kalmaz; kısmi ipucunda doğru örüntüye eğitim baseline'ından anlamlı ölçüde daha sık ulaşır.

## Aşama 17 — Matematik öğrenme arayüzü ve görev basamakları

**Amaç:** BrainNew'in nihai hedeflerinden biri olan matematik öğrenme kapasitesini, önceki öğrenme mekanizmalarını kullanarak sınamak.

Bu aşama, ağın matematik işlemlerini içine kodlamaz. Sayısal gösterim ve görev ortamı dış arayüzdür.

### Sayısal temsil

İlk tercih, tek bir nöronun “7” anlamına geldiği saf one-hot kod yerine, yakın sayıları örtüşen etkinlik örüntüleriyle temsil eden dağıtık/popülasyon kodlamasıdır.

- Sayı büyüklüğü, belirli bir reseptör nöronunun etkinliğiyle değil, bir nöron grubunun uzamsal/etkinlik örüntüsüyle temsil edilir.
- İki operand için ayrı girdi kanalları bulunur.
- Çıktı sayısı, motor organının okuduğu sıralı/örtüşen etkinlik örüntüsüyle temsil edilir.
- Kodlayıcı sayının kendisini ağa sunar; sonucu hesaplamaz.
- Çözücü etkinlik örüntüsünden ağın ürettiği sayısal cevabı okur; aritmetik işlemi yapmaz.
- Kodlama/çözme hataları ağın öğrenme performansından ayrı raporlanır.

### Matematik görev sırası

1. **M1 — Miktar/magnitude ayrımı:** Hangi sayı daha büyük? Yakın sayılarla karışma ölçülür.
2. **M2 — Sıralama ve ardışıklık:** Sayıların sırası ve ardışık ilişki öğrenilir.
3. **M3 — Küçük sayı toplama:** İki operanddan sonuç etkinlik örüntüsü üretme.
4. **M4 — Görülmemiş operand çiftleri:** Eğitimde sunulmayan kombinasyonlarda toplama genellemesi ölçülür.
5. **M5 — Çıkarma:** Benzer biçimde ayrı eğitim/test kümeleriyle sınanır.
6. **M6 — Daha geniş sayı aralığı ve çok basamaklı temsil:** Ancak küçük sayı görevlerinde gerçek genelleme gösterildikten sonra ele alınır.

### Eğitim ve geri bildirim

- Görev ortamı beklenen cevabı bilir; BrainNew'in içine cevabı doğrudan yazmaz.
- Ağın ürettiği çıktı motor organından okunur.
- Görev ortamı doğru/yanlış veya tanımlı bir başarı sinyali üretir.
- Bu sinyal yalnızca kimyasal/duyusal geri bildirim yolu üzerinden ağa döner.
- Görev ortamı sinaps ağırlığına, dendrit katkısına veya feedback dalına doğrudan dokunmaz.
- Testte ödül/ceza sinyali verilmez; ağ öğrendiği şeyi kendi başına göstermelidir.
- Test operand çiftleri eğitimde kullanılmaz; test kümesi hiperparametre ayarında kullanılmaz.

**Kabul ölçütü:** Ağ, eğitimde görülmeyen operand çiftlerinde başlangıç baseline'ından daha iyi sonuç verir. Eğitim örneklerini ezberlemek tek başına matematik öğrenmesi sayılmaz. Genelleme oluşmazsa sonuç açıkça raporlanır; test kümesine göre kural eklenmez.

## Aşama 18 — Uzun süreli öğrenme, unutma ve ardışık görevler

**Amaç:** Yeni öğrenmenin eski öğrenmeyi nasıl etkilediğini ölçmek.

Yapılacaklar:
- Aynı ağa önce bir ilişki/görev, sonra farklı bir görev öğretilecek.
- Eski görev performansı yeni görev öncesi ve sonrasında ölçülecek.
- Bağlantı budaması, homeostaz ve yeni bağlantı oluşumunun eski hafızayı nasıl etkilediği izlenecek.
- Gerektiğinde eski örüntüyü tekrar sunmanın pekiştirme etkisi ölçülecek.
- Episode izleri ile kalıcı öğrenilmiş parametreler ayrı raporlanacak.
- Unutma saklanmayacak; görevler arası performans matrisi tutulacak.

**Kabul ölçütü:** Eski ve yeni görev performansları ayrı raporlanır; unutma oranı ve bağlantı değişimleri ilişkilendirilebilir; tek bir toplam puan başarısızlığı gizlemez.

## Aşama 19 — Ablasyon, kalibrasyon ve bilimsel değerlendirme

**Amaç:** Hangi mekanizmanın hangi davranışa katkı verdiğini ayırmak.

Ablasyon koşulları:
- Dendrit-terminal katkı öğrenmesi kapalı.
- Hebbian/STDP kapalı.
- Uygunluk izi/modülatör kapalı.
- Feedback yayılımı kapalı.
- Sinaps-sinaps ilişkileri kapalı.
- Nöron-nöron etkileşimi kapalı.
- Kimyasal modülasyon kapalı.
- Mikroglia/yapısal plastisite kapalı.
- Homeostaz kapalı.

Her koşul:
- Aynı ağ topolojisi,
- Aynı başlangıç parametreleri,
- Aynı seed,
- Aynı eğitim sırası,
- Aynı test kümesi
ile karşılaştırılacak.

Kalibrasyon:
- Önce tek mekanizma, sonra mekanizma birleşimleri ayarlanacak.
- Test kümesi parametre ayarı için kullanılmayacak.
- Birden fazla seed çalıştırılacak.
- Ortalama yanında dağılım, en kötü ve en iyi koşular raporlanacak.
- Ağırlık doygunluğu, sessiz nöron, aşırı etkin nöron, bağlantı sayısı ve öğrenme süresi ölçülecek.
- Parametreler biyolojik sabit diye sunulmayacak; simülasyon ölçeğinde kalibre edilen değerler olarak tutulacak.

**Kabul ölçütü:** Her mekanizmanın katkısı ölçülür. Hiçbir görevde katkısı gösterilemeyen karmaşıklık yeniden değerlendirilir; yalnızca daha fazla mekanizma eklemek başarı sayılmaz.

## Aşama 20 — Performans, bellek ve son mimari dondurma

**Amaç:** Davranışı koruyarak simülasyonu büyütülebilir hâle getirmek.

Yapılacaklar:
- Olay tabanlı işleme ve lazy sönüm korunacak.
- Sinaps-sinaps ve nöron-nöron ilişkileri seyrek tutulacak.
- Yerel aday araması uzamsal indeksle yapılacak.
- Kimyasal alan kaynaklarının yaşam döngüsü sınırlandırılacak.
- Olay kuyruğunda geçersizleşmiş olaylar güvenli biçimde atılacak.
- Bellek ve çalışma süresi küçük, orta ve büyük ağlarda ölçülecek.
- Performans optimizasyonu matematiksel/işlevsel davranışı değiştirmeyecek.
- Bütün parametreler tek yapılandırma/deney anlık görüntüsünde kaydedilecek.
- Mimari, açık kararlar, varsayımlar, formüller, testler ve deney sonuçları belgelenerek dondurulacak.

**Kabul ölçütü:** Aynı seed ile deterministik davranış korunur; küçük ağdaki referans davranış ile optimize sürüm karşılaştırılır; ölçülmemiş performans iddiası yapılmaz; yeni geliştirici öğrenme kurallarının sahipliğini ve olay akışını anlayabilir.

---

# 4. Matematiksel sözleşme: parametre sınıfları

Sprintte bütün parametreler tek bir “ağırlık” kavramına indirgenmeyecek.

| Parametre | Anlamı | Sahibi | Zaman ölçeği |
|---|---|---|---|
| Nöron membran potansiyeli | Nöronun anlık elektriksel durumu | Noron | Hızlı |
| Nöron ateşlenme eşiği | Nöronun aksiyon potansiyeli koşulu | Noron | Hızlı/orta; homeostaz yavaşça değiştirir |
| Sinaps yerel potansiyeli | Çıkış terminalinin ateşlenmeye hazır olma durumu | Baglanti | Hızlı |
| Sinaps aktivasyon eşiği | Nöron ateşlendiğinde terminalin seçilme koşulu | Baglanti | Orta; feedback etkileyebilir |
| Gerçek sinaptik etkinlik katsayısı | Pre→post elektriksel etkinin kalıcı gücü/işareti | Baglanti | Öğrenmeyle değişir |
| Dendrit-terminal katkısı | Nöron içi yönlendirme etkisi | Dendrid | Öğrenmeyle değişir |
| Pre/post izleri | Kısa süreli zaman ilişkisi | Baglanti | Kısa |
| Uygunluk izi | Gecikmiş feedback için yerel geçmiş işareti | Baglanti | Orta |
| Sinaps-sinaps ilişkisi | Aynı nörondaki iki terminal arasındaki yönlü öğrenilmiş etki | Yerel nöron/sinaps ilişkisi | Orta/uzun |
| Nöron-nöron ilişkisi | Yakın nöronların birlikte etkinlik geçmişi | Yerel nöron ilişkisi | Orta/uzun |
| Yapısal bütünlük | Bağlantının fiziksel korunma durumu | Durum Baglanti üzerinde; karar Mikroglia'da | Uzun |
| Kimyasal yoğunluk | Tür bazında uzamsal-zamansal sinyal | KimyasalAlan | Türüne göre |
| Reseptör duyarlılığı | Dendritin kimyasal sinyale verdiği işaretli yanıt | Dendrid | Orta/uzun |
| Mikroglia durumu | Yerel bakım ajanının tarama/etkinlik durumu | Mikroglia | Orta/uzun |

Her öğrenilebilir parametre için:
- Alt/üst sınır,
- Güncelleme yönü,
- Güncelleme büyüklüğü,
- Sınıra yaklaşma davranışı,
- Güncelleme sahibi,
- Güncelleme olayı,
- Sönüm veya kalıcılık süresi
tanımlanmadan kodlanmayacaktır.

---

# 5. Deney ve ölçüm protokolü

Her deney kaydı en az şunları taşıyacak:

- Deney adı ve sürümü.
- Kod commit'i.
- Seed.
- Ağ konfigürasyonu ve topoloji özeti.
- Aktif/kapalı mekanizmalar.
- Eğitim, doğrulama ve test kümesi kimlikleri.
- Episode sırası ve simülasyon süresi.
- Girdi dizileri ve motor organının çıktıları.
- Doğru/yanlış yanıtlar.
- Nöron ateşlenme sayıları/oranları.
- Sinaptik ağırlıkların ve eşiklerin dağılımı.
- Dendrit katkılarının dağılımı.
- Uygunluk izi ve feedback olayları.
- Kimyasal kaynak sayısı ve reseptör yanıtı.
- Bağlantı oluşumu, olgunlaşması, onarımı ve kopması.
- Eğitim-test farkı, genelleme ve unutma ölçümleri.
- Olay sayısı, çalışma süresi ve bellek maliyeti.

Davranış ölçütleri:
- Tam eşleşme oranı.
- Doğru pozitif/yanlış pozitif/yanlış negatif.
- Sıra ayrımı.
- Örüntü tamamlama.
- Görülmemiş örnek genellemesi.
- Eski-yeni görev performans matrisi.
- Seed'ler arası dağılım.

Tek başarılı koşu yeterli değildir. İlk birim testlerinde tek seed deterministikliği doğrulamak için kullanılabilir; genelleme iddiası birden fazla seed gerektirir.

---

# 6. Test stratejisi ve son doğrulama

Testler yalnızca kodu yeşile çevirmek için değil, mimari kararların korunup korunmadığını göstermek için yazılacak.

Test katmanları:
1. **Birim:** Her yerel mekanizma kendi başına doğru çalışıyor mu?
2. **Olay entegrasyonu:** Aynı zamanlı olaylar ve gecikmeler doğru sırada mı?
3. **Öğrenme entegrasyonu:** Aynı ağ birden fazla episode boyunca öğrenilmiş durumunu koruyor mu?
4. **Davranış deneyi:** Ağ ilişki, sıra, geri çağırma ve matematik görevlerinde gelişme gösteriyor mu?
5. **Ablasyon:** Bir mekanizma kapatılınca beklenen davranış farkı oluşuyor mu?
6. **Deterministik tekrar:** Aynı seed aynı sonuçları üretiyor mu?
7. **Ölçek:** Ağ büyüdüğünde zaman/bellek maliyeti nasıl değişiyor?

Son sprint doğrulaması:
- Tam birim test paketi.
- Ana prototip smoke testi.
- Her öğrenme görevi için baseline/eğitim/test karşılaştırması.
- En az birkaç farklı seed ile genelleme raporu.
- Ablasyon tablosu.
- Performans/bellek tablosu.
- Açık kalan konular listesi.

Test çalıştırılmadan “geçti” denmeyecek. GitHub Actions runner'ı başlatılmazsa bu durum test başarısızlığı değil, testin çalıştırılamaması olarak raporlanacak; yerel çalıştırma çıktısı ayrıca alınacak.

---

# 7. Biyolojik dayanak ve soyutlama sınırı

Aşağıdaki kaynaklar modelin biyolojik esinini destekler; BrainNew'in her denkleminin gerçek biyolojiyi birebir temsil ettiği anlamına gelmez.

- **STDP ve zamanlama:** Debanne & Inglebert (2023), *Spike timing-dependent plasticity and memory*, Current Opinion in Neurobiology. STDP'nin pre/post zaman sırasına bağlı olduğunu; fakat biyolojik plastisitenin yalnızca spike zamanlamasından ibaret olmadığını tartışır. https://doi.org/10.1016/j.conb.2023.102707
- **Gecikmiş ödül ve uygunluk izleri:** Shouval & Kirkwood (2025), *Eligibility traces as a synaptic substrate for learning*. Uygunluk izlerinin gecikmiş ödülle kalıcı plastisiteye dönüşmesini ve LTP/LTD dengesinin önemini ele alır. https://doi.org/10.1016/j.conb.2025.102978
- **Üç faktörlü öğrenme:** Gerstner ve diğerlerinin üç faktörlü plastisite literatürü, yerel pre/post etkinliğe ek üçüncü modülatörün gecikmiş öğrenmeye katkısını inceler. https://pubmed.ncbi.nlm.nih.gov/30108488/
- **Mikroglia:** *Microglia: Activity-dependent regulators of neural circuits* (2024), mikroglianın aktiviteyi algılayıp devre ve sinaps işlevini düzenleyebildiğini özetler. https://doi.org/10.1111/nyas.15105
- **Sinaptik budama:** *Molecular mechanisms underlying microglial sensing and phagocytosis in synaptic pruning*; etkinlik, işaretleme ve koruyucu sinyallerin birlikte rolünü inceler. https://pmc.ncbi.nlm.nih.gov/articles/PMC11467947/
- **Hacimsel iletim:** Özçete ve diğerleri (2024), *Mechanisms of neuromodulatory volume transmission*. Yayılım, geri alım, yıkım, salım bölgeleri ve reseptör konumlarının kimyasal sinyalin uzay-zaman profilini belirlediğini tartışır. https://pmc.ncbi.nlm.nih.gov/articles/PMC11540752/
- **Homeostaz ve uyarılma/baskılanma dengesi:** *Homeostatic plasticity and excitation-inhibition balance: The good, the bad and the ugly* (2022). Ateşlenme hedefi ve devre kararlılığı arasındaki ilişkiyi inceler. https://pmc.ncbi.nlm.nih.gov/articles/PMC9477500/

Bu literatürden çıkarılacak ilke “beyni aynen kopyala” değildir. Her biyolojik mekanizma, BrainNew'in amacına hizmet ettiği ölçüde ve hesaplama maliyeti karşılanabildiği ölçüde soyutlanacaktır.

---

# 8. Uygulama sırası ve bağımlılık özeti

Önerilen sıra:

`Sözleşme → Olay doğruluğu → Sayısal güvenlik → Ağ kurucu → Girdi/çıktı → Kalıcı eğitim → Baseline → Sinaptik plastisite → Uygunluk/modülatör → Dallanmış feedback → Sinaps-sinaps → Nöron-nöron → Kimyasal sistem → Mikroglia/yapısal yaşam döngüsü → Homeostaz → Geri çağırma → Matematik → Uzun dönem öğrenme → Ablasyon → Performans/dondurma`

Bu sıranın nedeni:
- Eğitim yürütücüsü olmadan öğrenme iddiası ölçülemez.
- Baseline olmadan öğrenme kazanımı hesaplanamaz.
- Olay ve zaman doğruluğu olmadan STDP/eligibility/feedback güvenilir değildir.
- Girdi/çıktı temsili olmadan matematik görevi kurulamaz.
- Sinaps-sinaps ve nöron-nöron etkileşimi, temel bağlantı ve iz yaşam döngüsü sağlamlaşmadan eklenirse hatanın kaynağı ayırt edilemez.
- Yapısal plastisite, işlevsel öğrenme ölçümleriyle birlikte değerlendirilmelidir.
- Matematik görevleri, basit ilişki ve sıra öğrenmesi kanıtlanmadan erken başlatılmamalıdır.

---

# 9. Sprintin nihai teslimatı

Sprint tamamlandığında depoda şu bütünlük bulunmalı:

- Güncel mimari sözleşmesi.
- Tek ve tutarlı öğrenme değişkenleri/sahiplik tablosu.
- Deterministik ağ kurucu.
- Reseptör ve motor organları.
- Baseline yürütücüsü ve kalıcı eğitim yürütücüsü.
- Episode yaşam döngüsü.
- Yerel sinaptik öğrenme, STDP, uygunluk izi ve modülatör.
- Kullanıcının feedback eşik kuralı ve dallanan feedback.
- Sinaps-sinaps ve nöron-nöron yerel etkileşimleri.
- Kimyasal sinyal ve reseptör sistemi.
- Bağımsız mikroglia, bağlantı bakımı, onarımı, budaması, büyümesi ve olgunlaşması.
- Homeostaz.
- Örüntü geri çağırma ve genelleme deneyleri.
- Matematiksel temsil ve kademeli görev ailesi.
- Ablasyon, deterministik tekrar ve performans raporu.
- Tam test paketi ve test çalıştırma kayıtları.

**Sprintin gerçek başarı ölçütü:** BrainNew'in sinaps ağırlıklarını değiştirmesi değil; aynı ağın deneyimden sonra davranışını kalıcı biçimde değiştirmesi, bu değişimin yerel mekanizmalardan kaynaklanması, kısmi ipucuyla öğrendiğini geri çağırabilmesi ve daha önce görmediği örneklerde genelleme başarısının ölçülebilmesidir.
