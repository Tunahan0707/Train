# Yerel Dendrit-Sinaps Dinamikleri — Tasarım

Bu belge experiment/dendritic-synaptic-potentials dalındaki sıfırdan başlatılan yeni BrainNew tasarımının güncel tasarım sözleşmesidir. Eski fix/synaptic-contribution-tracking dalı bu tasarımın çalışma dalı değildir.

Belgede kararlar, öneriler ve açık araştırma noktaları birbirinden ayrılır. Sayısal değerlerin deneysel olarak belirlenmesi gereken yerlerde geçici örnekler kesin karar gibi sunulmaz. Bu belge tasarımı tanımlar; çalışan entegrasyon veya test başarısı iddiası değildir.

## 1. Temel mimari ve nöronun çalışma döngüsü

- Beyin yalnızca simülasyon zamanını ve bileşenler arası koordinasyonu yöneten orkestratördür.
- Öğrenme, geri bildirimin yerel değerlendirilmesi ve sinaptik değişiklik kararları nöronlar/yerel mekanizmalar tarafından verilir. Beyin hangi sinapsın değişeceğine veya feedback'in ne anlama geldiğine karar vermez.
- Nöronun aksiyon potansiyeli oluşturması, o nörona ait bütün sinapsların koşulsuz biçimde aktive olması anlamına gelmez.
- Aksiyon potansiyeli oluştuğunda, yalnızca kendi yerel durumları ve aktivasyon koşulları uygun olan sinapslar aktive olabilir. Aktivasyon potansiyelinin/eşiğinin aşılmış olması tek başına sinapsı otomatik aktive etmez; nöronun aksiyon potansiyeli oluşturması gerekir.
- Nöronun çalışma döngüsünde aksiyon potansiyeli, dinlenme ve yeniden polarizasyon aşamaları bulunur. Döngü tamamlandığında nöron yeni sinyale hazır hâle gelir.
- Aksiyon potansiyeli tamamlandığında sinyal dalga biçiminde gönderilir. Bu dalganın uzamsal/zamansal yayılım ayrıntıları ayrıca modellenebilir.
- Aksiyon potansiyelinden sonra refrakter dönem modellenir. Eski branch'de depolarizasyon, repolarizasyon ve hiperpolarizasyon durumları boyunca yeni ateşlenme kararı engellenir. Mutlak ve göreli refrakter dönemlerin ayrı ayrı modellenmesi yeni tasarımda ayrıca kararlaştırılacaktır. Sinaptik girdilerin alınması ile yeniden ateşlenmek ayrı olaylardır.


### 1.1. Eski branch'den korunan membran ve aksiyon potansiyeli mekanizması

`fix/synaptic-contribution-tracking` branch'indeki `Noron.py`, `Dendrid.py` ve ilgili testler incelendi. Aşağıdaki mekanizma önceki tasarımın mevcut davranışıdır ve yeni tasarımda başlangıç referansı olarak korunacaktır. Bu bölümün eklenmesi, yeni yerel sinaps dinamikleriyle entegrasyonun tamamlandığı anlamına gelmez.

Eski mekanizmada nöronun ateşlenme kararı, dendritlerden toplanan toplam etkinin nöron membran potansiyeline uygulanması ve bu potansiyelin eşik değerine ulaşması üzerinden verilir:

- Dinlenme membran potansiyeli: -70 mV.
- Ateşlenme eşiği: -55 mV.
- Depolarizasyon durumunda membran potansiyeli +30 mV yapılır.
- Sonraki adımda repolarizasyon durumunda -40 mV yapılır.
- Ardından hiperpolarizasyon durumunda -80 mV değerine geçilir ve 2 zaman adımı beklenir.
- Hiperpolarizasyon tamamlanınca nöron dinlenme durumuna ve -70 mV değerine döner.
- Dinlenme durumunda dendritlerden alınan toplam etki membran potansiyeline eklenir. Ardından potansiyel dinlenme değerine doğru sızıntı oranı kadar çekilir.
- Eski kodun varsayılan sızıntı oranı 0.05'tir. Bu oran ve yukarıdaki mV değerleri eski uygulamanın başlangıç parametreleridir; yeni modelde deneysel doğrulama olmadan biyolojik sabit sayılmaz.
- Pozitif ve negatif sinaptik etkiler aynı toplamda yer alır; uyarıcı etkiler membran potansiyelini yükseltirken baskılayıcı etkiler düşürür.
- Dış duyusal girdi eski kodda doğrudan membran potansiyeline etki eder ve yalnızca nöron dinlenme durumundayken uygulanır.
- Eski uygulamada nöron dinlenme dışındaki tüm durumlarda yeni ateşlenme kararı vermez. Bu, tek bir refrakter/durum döngüsüdür; mutlak ve göreli refrakter dönemlerin ayrı fizyolojik mekanizmalar olarak uygulanmış olduğu anlamına gelmez.

Eski uygulamada bağlantıdan gelen etkiler dendritte bekletilir, nöronun dinlenme adımında dendritlerden alınarak membran potansiyeline eklenir. Ateşlenme anında o ana kadar birikmiş ve katkıda bulunan bağlantılar uygunluk izi kazanır. Eski modelde her ateşlenme, nöronun bütün akson bağlantıları üzerinden iletim planlanmasına yol açar.

**Yeni tasarımla entegrasyon için önemli ayrım:** Eski modelde bağlantı etkisi doğrudan dendrit ve oradan membran potansiyeline gider; yeni tasarımda ise dendrit-sinaps çiftlerinin ayrı yerel potansiyelleri ve sinapsların seçici aktivasyonu bulunur. Bu nedenle eski membran toplama mekanizmasının korunması, yerel sinaps potansiyellerinin membran potansiyeline hangi aşamada ve hangi kuralla katkı vereceğinin ayrıca tanımlanmasını gerektirir. Yerel sinaps potansiyelinin eşiği aşması tek başına nöronu ateşletmez; nöronun ateşlenme kararı membran potansiyeli/eşik mekanizmasında kalır.

## 2. Dendrit-sinaps etkileşimi ve yerel potansiyel

### 2.1. Toplamsal dendrit katkıları

Her dendrit, hedef nörona gelen sinapsların her birine ayrı bir yerel potansiyel katkısı yükleyebilir. Dendrit-sinaps ilişkisi çarpımsal bir öğrenme katsayısının güncellenmesi olarak tanımlanmaz; her dendrit-sinaps çifti için ayrı, toplamsal bir katkı/değer bulunur.

- Bir dendrit yalnızca gerçekten potansiyel yüklediği sinaps için bu etkileşimin öğrenme güncellemesine katılır.
- Sinaps, ilgili değerlendirme/aktivasyon fırsatında aktive olursa o dendritin ilgili sinaps üzerindeki katkısı küçük bir pozitif yönde güncellenir.
- Sinaps aktive olmazsa katkı küçük bir negatif yönde güncellenir.
- Dendrit o sinapsa potansiyel yüklememişse bu kurala göre güncelleme yapılmaz.
- Güncellemenin büyüklüğü, ilgili sinapsın en son ne zaman ateşlendiğine bağlı olabilir. Yakın zamanda ateşlenmiş sinapslarda güncelleme daha belirgin; uzun süredir ateşlenmemiş sinapslarda etki olabildiğince küçük olacak şekilde tasarlanır.
- Bu zaman bağımlılığının matematiksel fonksiyonu ve pozitif/negatif adımların büyüklükleri henüz belirlenmemiştir.

Birden fazla dendrit aynı sinapsa toplamsal katkı yüklediğinde, toplam etkinin etkin dendrit sayısı dikkate alınarak normalize edilmesi mümkündür. Böylece yalnızca etkin dendrit sayısının artması nedeniyle sinaps potansiyelinin kontrolsüz büyümesi önlenebilir. Normalizasyonun paydası, hangi dendritlerin sayılacağı ve bunun zaman adımına mı yoksa sinapsa yüklenen katkı sayısına mı göre yapılacağı deneysel olarak netleştirilecektir.

### 2.2. Sinapsın yerel durumu ve aktivasyon koşulu

Her sinaps en azından şu yerel bilgileri taşır:
- yerel aktivasyon potansiyeli,
- aktivasyon/uygunluk eşiği veya koşulu,
- geçici etkinlik izi,
- son aktive olma/ateşlenme zamanı,
- yapısal bağlantı durumu ve bağlantı dayanıklılığı/kullanılmama geçmişi.

Dendrit katkıları, sinaps-sinaps etkileşimleri ve feedback sinapsın yerel potansiyelini etkileyebilir. Ancak yerel potansiyelin eşiği aşması tek başına aktivasyon başlatmaz. Sinapsın aktive olabilmesi için nöronun aksiyon potansiyeli oluşturduğu aşamada aktivasyon koşullarının uygun olması gerekir. Hangi sinapsların bu koşulları sağladığı yerel olarak belirlenir.

### 2.3. Hiç ateşlenmemiş sinapslar

Hiç ateşlenmemiş bir sinapsın son ateşlenme zamanı bulunmaz. Bu durum için başlangıçta nötr davranış, ilk aktivasyon girişimine kadar negatif güncelleme yapmama veya küçük başlangıç yanlılığı seçenekleri arasında henüz karar verilmemiştir. Bu durum, yakın zamanda ateşlenmemiş fakat geçmişte ateşlenmiş sinapslarla aynı kabul edilmeyecektir.

## 3. Sinaps-sinaps etkileşimi

Sinaps-sinaps etkileşimleri aynı nörona ait sinapslar arasında yerel ve yönlüdür. Başlangıçta öğrenilmiş bir ilişki bulunmaz; etkileşimler kullanım/öğrenme sonucunda oluşur. Her olası sinaps çifti için baştan yoğun bir bağlantı matrisi oluşturmak yerine yalnızca oluşmuş/öğrenilmiş ilişkilerin saklanması tercih edilir.

- Sinaps k etkinleştiğinde, k→j yönündeki öğrenilmiş ilişki üzerinden aynı nörondaki j sinapsının yerel potansiyeline geçici etki aktarabilir.
- Kendine etki (k=j) yoktur.
- k→j ile j→k ayrı ilişkilerdir; biri diğerini zorunlu olarak belirlemez.
- Birlikte etkinleşme, ilgili yönlü ilişkiyi küçük bir miktar artırabilir.
- Birlikte etkinleşmeme durumunda ilişkinin azaltılması mı, yoksa değişmeden bırakılması mı gerektiği henüz kesinleştirilmemiştir.
- İlişkilerin sonlu aralıkta kalması gerekir; sınırlar ve güncelleme miktarları deneysel olarak belirlenecektir.
- Geçici potansiyel aktarımı ile kalıcı öğrenilmiş ilişkinin güncellenmesi birbirinden ayrı tutulur.
- Güncellemelerin yalnızca ilgili yerel olaylarda yapılması, bütün sinaps çiftlerinin her zaman adımında taranmaması tercih edilir.

Birlikte etkinleşmenin zaman penceresi, negatif ilişkinin öğrenilip öğrenilemeyeceği ve ilişkinin güncelleme zamanlaması açık araştırma konularıdır.

## 4. Geçici etkinlik izi

Her sinaps etkinleştiğinde geçici etkinlik izi artar ve zamanla azalır. İz:
1. Feedback'in geriye doğru hangi dallardan ilerleyebileceğini değerlendirmede,
2. Yerel etkinlik geçmişini belirlemede,
3. Sinaps-sinaps birlikte etkinleşme ilişkilerini değerlendirmede
kullanılır.

İz tek başına kalıcı öğrenme değildir. Deneme/episode sonunda temizlenebilir; öğrenilmiş ilişkiler ve yapısal bağlantılar bundan ayrı tutulur.

Feedback için ayrıca kalıcı bir nedensel yol/iz (track) veri yapısı tutulması zorunlu değildir. Geriye dönük erişim geçici etkinlik izleri ve güncel adım verileri üzerinden sağlanır.

## 5. Geri bildirim ve yayılım

### 5.1. Geriye doğru dallanma

Feedback, yerel etkinlik izleri ve güncel adım verileri üzerinden geriye doğru takip edilebilen dallara yayılabilir. Her dal kendi izine göre bağımsız değerlendirilir.
- Bir dal, kendi etkinlik izi ilgili geri-adım eşiğinin altına düştüğünde durur.
- Bir dalın durması diğer dalların ilerlemesini durdurmaz.
- Sabit maksimum derinlik temel durdurma kuralı değildir; dal bazındaki iz eşiği esastır.
- Geriye doğru her adımda etkinin büyüklüğü azalır.
- Dalların iz eşiğinin ve adım başına azalma katsayısının matematiksel biçimi henüz kalibre edilmemiştir.

### 5.2. Etkilerin ayrı ayrı uygulanması

Aynı feedback yayılımında farklı dallardan aynı yerel elemana ulaşan etkiler birleştirilip tek bir toplam etki olarak uygulanmaz. Her katkı ayrı ayrı ve sırayla uygulanır. Bu nedenle uygulama sırası nihai potansiyeli etkileyebilir; sıra belirleme/işleme politikası ayrıca tanımlanmalıdır.

### 5.3. Potansiyel üzerindeki etki ve sınırlar

Feedback yalnızca ateşlenme/aktivasyon potansiyellerini küçük miktarlarda etkiler. Feedback'in dendrit-sinaps öğrenilmiş katkılarını, sinaps eşiklerini veya diğer kalıcı öğrenilmiş parametreleri doğrudan güncellediği kabul edilmez.

- Potansiyelin dış sınırları [-1,+1] olarak belirlenmiştir.
- Bu iki değer potansiyelin yakınsaması gereken hedef değerler değil, aşılmaması gereken dış sınırlardır.
- Potansiyel mevcut değerine ve sınırlara yakınlığına bağlı olarak feedback etkisinin büyüklüğü ölçeklenebilir.
- Etkiler toplamsal biçimde ayrı ayrı uygulandığından, ölçekleme her bir etki uygulanırken o andaki güncel potansiyel üzerinden değerlendirilmelidir.
- Kullanılacak ölçekleme fonksiyonu, büyük bir etki altında dahi sınırların aşılmasını matematiksel olarak garanti etmelidir. Önceki doğrusal ölçekleme önerisi bu garantiyi tek başına sağlamadığından kesin çözüm olarak kabul edilmemiştir.
- Potansiyelin hangi iç değerlere/denge noktalarına yaklaşacağı henüz belirlenmemiştir; deneysel olarak konuşulacaktır.
- Yakın zamanda ateşlenmemiş nöronlar üzerindeki etkinin olabildiğince minimal tutulması hedeflenir. Bu etkinin hangi yerel mekanizmalara ve hangi zaman ölçeğine uygulanacağı ayrıca kalibre edilecektir.

Pozitif/negatif feedback'in etkinlik izi bulunan ve bulunmayan yerel konumlara uygulayacağı kolaylaştırıcı/engelleyici etki yönleri önceki tabloda önerilmişti; bu yönlerin tümü nihai matematiksel kural olarak sabitlenmiş sayılmaz. Özellikle hiç ateşlenmemiş sinapsların davranışı ayrı ele alınmalıdır.

## 6. Bağlantı sınıfı, nörotransmitterler ve mikroglia-benzeri kontrol

- Mikroglia-benzeri kontrol ayrı ve merkezi bir karar katmanı olarak değil, bağlantı sınıfı/nesnesi üzerinden yönetilecektir.
- Nörotransmitterler bağlantı üzerinden geçer; etkileri bağlantının kendisi üzerinde ortaya çıkar.
- Bağlantının korunması, zayıflaması, yeniden şekillenmesi ve fiziksel olarak koparılması bu bağlantı-yerel mekanizma içinde ele alınır.
- Bağlantının zayıflaması ile bağlantının fiziksel olarak ortadan kaldırılması ayrı olaylardır.
- Mikroglia-benzeri kontrolün iç durumu, hangi sinyallere nasıl tepki verdiği ve budama/koruma kuralları henüz ayrıntılandırılmamıştır.

Kimyasal sinyalleşme yerel olmalıdır. Birden fazla nörotransmitter türü aynı anda bulunabilir; dendritlerdeki reseptör-benzeri duyarlılıklar farklı transmitter türlerine farklı yanıtlar verebilir. Kimyasal sinyaller yerel elektriksel davranışı ve plastisiteyi modüle eder; tek başlarına “şu sinapsı güçlendir” şeklinde merkezi bir öğrenme komutu değildir. Sinyalin hangi bileşenler arasında ve bağlantı nesnesinin hangi iç mekanizması üzerinden taşınacağı tasarımın ilgili yerel kurallarıyla belirlenir.

## 7. Bağlantı yaşlanması, kopma ve yeniden bağlantı

### 7.1. Kullanılmayan bağlantıların yaşlanması

Kullanılmayan bağlantılar zamanla zayıflayabilir/yaşlanabilir. Kullanım bağlantının kullanılmama geçmişini sıfırlayabilir veya dayanıklılığını destekleyebilir. Yaşlanma:
- bir anda silme şeklinde değil, kademeli olmalı,
- aktif bağlantıların ömrünü uzatmalı,
- tek bir denemede kullanılmadı diye bağlantıyı silmemeli,
- simülasyon adımıyla ölçeklenmelidir.

Önceki taslakta dayanıklılık 1.0, kullanılmama başına 0.9995 çarpanı ve 0.1 kopma sınırı örnek kalibrasyon değerleri olarak önerilmişti. Bunlar biyolojik sabit veya kesin karar değildir; testlerle doğrulanmadan zorunlu parametre olarak kullanılmamalıdır.

### 7.2. Yeni bağlantı oluşumu

Bağlantısız bir akson terminalinin yeni bağlantı kurması mümkün olmalıdır. Yeni bağlantı arayışında:
- Uzamsal konum kullanılarak uygun/boşta bir dendrit aranır.
- Bağlantısız terminalin aktivasyon girişimi, belirli bir nörotransmitterin etkisi altındaysa bağlantı oluşumunu tetikleyebilir.
- Doğrudan aktivasyon girişimi de yeni bağlantı oluşumuna yol açabilecek bir koşuldur.
- Bağlantı kurulacak dendritin uygun/boşta olması gerekir; rastgele tüm ağdan hedef seçilmez.

Hangi nörotransmitterin hangi koşulda etkili olacağı, doğrudan aktivasyon girişiminin tam anlamı, arama yarıçapı, adayın yaşam döngüsü ve yeni bağlantının başlangıç özellikleri henüz belirlenmemiştir. Yeni bağlantının başlangıçta zayıf/kararsız olması bir tasarım önerisidir; kesin başlangıç parametreleri açık konudur.

### 7.3. Bağlantısını kaybeden nöronun toparlanması

Bağlantısını kaybeden nöronun yeniden bağlantı kurabilmesini ve plastisitesini desteklemek için:
- Nörona genel/yerel mekanizmalardan pozitif etki verilmesi,
- Ateşlenme potansiyelinin varsayılan bir değere döndürülmesi
önerilmiştir.

Bu toparlanma davranışının kapsamı henüz kesinleşmemiştir: bir bağlantının kaybı mı, nöronun tüm bağlantılarını kaybetmesi mi tetikleyicidir; pozitif etki yalnızca yeniden bağlantı ararken mi sürer, yoksa yeni bağlantıdan sonra da bir süre devam mı eder? Bu sorular açık bırakılmıştır. Bu mekanizma, bağlantısını kaybeden her nörona sürekli ve sınırsız pozitif bias verilmesi şeklinde varsayılmamalıdır.

## 8. Başlangıç parametreleri ve kalibrasyon

Aşağıdakiler kesin biyolojik sabitler değildir; prototipte deneyle ayarlanacak başlangıç önerileridir:
- Dendrit-sinaps katkılarının başlangıç dağılımı ve büyüklüğü: henüz belirlenmedi.
- Dendrit katkılarının pozitif/negatif güncelleme miktarı: henüz belirlenmedi.
- Son ateşlenme zamanına bağlı güncelleme fonksiyonu: henüz belirlenmedi.
- Etkin dendrit sayısına göre normalizasyon: prensip olarak değerlendirilecek; kesin formu belirlenmedi.
- Sinapslar arası öğrenilmiş ilişkiler: başlangıçta ilişki bulunmaması; yalnızca oluşmuş ilişkilerin saklanması.
- Sinaps yerel potansiyelinin dış sınırları: [-1,+1].
- Feedback'in potansiyel üzerindeki tekil etki büyüklükleri ve sınırda güvenli ölçekleme fonksiyonu: henüz belirlenmedi.
- Feedback'in geriye doğru adımlarda azalma katsayısı: henüz belirlenmedi.
- Sinaps aktivasyon koşulları/eşikleri: önceki taslakta önerilen 0.2–0.4 aralığı doğrulanmış karar değildir; yeni aktivasyon döngüsüyle birlikte yeniden kalibre edilmelidir.
- Geçici etkinlik izi sönümü: deneysel olarak belirlenecek.
- Bağlantı dayanıklılığı ve kullanılmama yaşlanması: deneysel olarak belirlenecek.
- Uzamsal temsilin 2B/3B seçimi ve bağlantı arama yarıçapı: henüz kesinleşmedi.

## 9. Zorunlu testler

1. Bir dendritin potansiyel katkısı yalnızca yükleme yaptığı hedef sinapsı etkiler.
2. Aynı anda birden fazla dendritin katkısı doğru biçimde hesaplanır ve normalizasyon seçeneği ayrı test edilir.
3. Bir dendritin ilgili sinapsa katkı yüklemediği durumda o dendrit-sinaps çifti için öğrenme güncellemesi yapılmaz.
4. Sinaps aktive olursa ilgili dendrit katkısı pozitif; aktive olmazsa negatif yönde küçük güncellenir.
5. Güncelleme büyüklüğü son ateşlenme zamanına bağlıdır; uzun süredir ateşlenmemiş sinaps üzerindeki etki minimal kalır.
6. Hiç ateşlenmemiş sinapsın davranışı, geçmişte ateşlenip uzun süredir ateşlenmeyen sinapstan ayrı test edilir.
7. Yerel potansiyeli aktivasyon seviyesini aşmış sinaps, nöron aksiyon potansiyeli oluşmadan otomatik aktive olmaz.
8. Nöron aksiyon potansiyeli oluşturduğunda yalnızca aktivasyon koşullarını sağlayan sinapslar aktive olabilir; uygun olmayan sinapslar zorla aktive edilmez.
9. Membran potansiyeli eşik altında kaldığında nöron ateşlenmez; eşik değerine ulaştığında ateşlenir.
10. Pozitif ve negatif dendritik/sinaptik etkiler membran potansiyelini doğru yönde değiştirir.
11. Membran potansiyelinin dinlenme değerine sızıntısı doğru uygulanır ve parametreleri kalibre edilebilir.
12. Depolarizasyon (+30 mV), repolarizasyon (-40 mV), hiperpolarizasyon (-80 mV / 2 adım) ve dinlenmeye dönüş döngüsü doğrulanır.
13. Refrakter durumlarda yeni ateşlenme kararı verilmez; bekleyen sinaptik girdilerin nasıl ele alınacağı açıkça test edilir.
14. Yeni tasarımda yerel sinaps potansiyellerinin membran potansiyeline katkı kuralı belirlendikten sonra, seçici sinaps aktivasyonu ile nöronun ateşlenme kararı birbirinden bağımsız test edilir.
15. Aksiyon potansiyeli tamamlandığında sinyal dalga biçiminde gönderilir.
12. Sinaps-sinaps etkileşimleri yönlüdür; k→j ile j→k bağımsız davranır.
13. Sinaps-sinaps geçici potansiyel aktarımı ile kalıcı ilişki öğrenmesi birbirinden ayrıdır.
14. Feedback bütün erişilebilir dalları bağımsız izler; bir dalın durması diğer dalları durdurmaz.
15. Aynı konuma ulaşan farklı feedback katkıları birleştirilmeden, ayrı ayrı ve sırayla uygulanır.
16. Feedback etkisi yalnızca potansiyelleri değiştirir; kalıcı dendrit katkılarını veya sinaps eşiklerini doğrudan değiştirmez.
17. Potansiyel [-1,+1] dışına çıkmaz; büyük tekil etkiler ve art arda uygulanan çoklu etkiler sınanır.
18. Potansiyel sınırlarına yaklaşırken etki ölçeklemesi güvenli çalışır; yakınsama hedefleri ayrıca deneysel olarak belirlenir.
19. Feedback yayılımında her adımda etki azalır ve dal kendi iz eşiğiyle durur.
20. Bağlantı üzerinden geçen nörotransmitterin bağlantı-yerel mekanizma üzerindeki etkisi doğrulanır.
21. Kullanılmayan bağlantıların yaşlanması ve yeniden kullanımda durumunun değişmesi test edilir.
22. Bağlantısız akson terminali, uzamsal aramayla uygun/boşta dendrit bulabilir.
23. Yeni bağlantı oluşumu belirli transmitter etkisi ve doğrudan aktivasyon girişimi koşulları için ayrı ayrı test edilir.
24. Bağlantısını kaybeden nöronun toparlanma mekanizması, tetikleyici ve süre kararları verildikten sonra test edilir.
25. Aynı seed ile aynı başlangıç koşulları tekrarlanabilir.

## 10. Açık araştırma ve karar noktaları

- Dendrit-sinaps toplamsal katkılarının veri temsili ve başlangıç dağılımı nasıl olacak?
- Etkin dendrit sayısına göre normalizasyonun kesin formu ne olacak?
- Son ateşlenme zamanına bağlı pozitif/negatif güncelleme fonksiyonu ne olacak?
- Hiç ateşlenmemiş sinaps ilk aktivasyon girişimine kadar nasıl davranacak?
- Eski branch'deki membran potansiyeli toplama/sızıntı/eşik mekanizması yeni yerel sinaps potansiyelleriyle nasıl bütünleştirilecek: yerel sinaps potansiyelleri dendrit üzerinden membrana hangi koşulda, ne kadar ve hangi zamanlamayla katkı verecek?
- Sinapsın yerel aktivasyon koşulu/eşiği ile nöronun membran potansiyeli üzerinden aksiyon potansiyeli oluşturma koşulu arasındaki kesin ilişki nasıl kurulacak?
- Eski modeldeki sabit +30/-40/-80 mV durum geçişleri ve 2 adımlık hiperpolarizasyon yeni simülasyon zaman ölçeğinde korunacak mı, yoksa kalibre edilecek mi?
- Refrakter dönem tek birleşik kilit olarak mı kalacak, yoksa mutlak ve göreli dönemler ayrı mı modellenmeli?
- Refrakter dönemde gelen sinaptik etkiler bekletilmeli, sönümlenmeli, yoksa başka bir yerel kurala mı tabi olmalı?
- Aksiyon potansiyeli dalgasının yayılımı ve terminal/bağlantı üzerindeki zamanlaması nasıl modellenmeli?
- Sinaps-sinaps ilişkisi hangi zaman penceresinde birlikte etkinleşme sayılmalı?
- Birlikte etkinleşmeme ilişkiyi azaltmalı mı, yoksa ilişki değişmeden mi kalmalı?
- Sinapslar arası negatif ilişkiler öğrenilebilmeli mi?
- Feedback dallarında aynı konumun tekrar ziyaret edilmesi ve uygulama sırasının belirlenmesi nasıl ele alınmalı?
- Feedback'in sınırları aşmasını kesin olarak önleyen fonksiyon ne olacak; potansiyelin deneysel yakınsama/denge değerleri ne olacak?
- Yakın zamanda ateşlenmemiş nöronlara minimal etki kuralı hangi mekanizmalara, hangi zaman ölçeğinde uygulanacak?
- Bağlantı nesnesinin mikroglia-benzeri kontrolü hangi iç durumları ve yerel kuralları içerecek?
- Bağlantı oluşumunu tetikleyebilecek nörotransmitter türü/türleri ve koşulları ne olacak?
- Uzamsal arama 2B mi 3B mi olacak; uygun dendrit arama yarıçapı ve konum modeli nasıl seçilecek?
- Bağlantısını kaybeden nöronun toparlanma mekanizması hangi bağlantı kaybı türünde başlayacak ve yeni bağlantı kurulduktan sonra ne kadar sürecek?
