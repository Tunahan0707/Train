# BrainNew — Yerel Sinaptik Dinamikler ve Nöral Ağ Tasarımı

Bu belge `experiment/dendritic-synaptic-potentials` branch'indeki BrainNew tasarım sözleşmesidir. Eski `fix/synaptic-contribution-tracking` branch'i yalnızca önceki membran/ateşlenme mekanizmasının referansı olarak incelenmiştir; bu branch yeni tasarımın çalışma dalı değildir.

Belgede üç ayrım korunur:
- **Kesin tasarım kararı:** Kullanıcı tarafından açıkça kabul edilmiş veya bu belge güncellemesinde mimari açıdan yeterince sağlam bulunarak sabitlenmiş kural.
- **Tasarım tercihi:** Uygulamada izlenecek güçlü öneri; sayısal kalibrasyon gerektirebilir.
- **Açık karar:** Önceki konuşmalarda ayrıntısı doğrulanamayan veya deney olmadan kesinleştirilmemesi gereken konu.

Bu belge tasarımı tanımlar; kodun uygulandığı veya testlerin geçtiği anlamına gelmez. Biyolojik esin ile biyolojik birebirlik aynı şey değildir. Matematiksel kolaylaştırmalar ayrıca belirtilir.

## 1. Temel mimari ve nöronun çalışma döngüsü

- Beyin yalnızca simülasyon zamanını, olay kuyruğunu ve bileşenler arası koordinasyonu yöneten orkestratördür.
- Öğrenme, geri bildirimin yorumlanması ve yerel bağlantı/sinaps değişikliği kararları nöronlar, dendritler, sinapslar, mikroglia-benzeri yerel yapılar ve bunların yerel etkileşimleri tarafından verilir. Beyin hangi sinapsın değişeceğine karar vermez.
- Yerel ve olay-tabanlı etkileşimler tercih edilir. Bütün ağın her zaman adımında taranması veya tüm olası sinaps çiftleri için yoğun matris tutulması temel yöntem olmayacaktır.
- Nöronun aksiyon potansiyeli oluşturması, o nörona ait bütün çıkış sinapslarının koşulsuz aktive olması anlamına gelmez.
- Bir nöron aksiyon potansiyeli oluşturduğunda yalnızca yerel aktivasyon potansiyeli kendi eşiğini karşılayan çıkış sinapsları aktive olur. Yerel sinaps potansiyelinin eşiği aşması tek başına aksiyon potansiyeli oluşturmaz.
- Sinaptik girdiyi almak, membran potansiyelini değiştirmek, nöronun ateşlenmesi ve nöronun çıkış sinapslarının aktive olması ayrı olaylardır.
- Nöron ateşlenme döngüsü tamamlanmadan yeniden ateşlenemez. Refrakter dönem sırasında gelen girdilerin nasıl saklanacağı veya sönümleneceği ayrıca tanımlanır.
- Aksiyon potansiyeli başlatıldığında çıkış sinapslarının uygun olanları aynı ateşlenme olayında aktive edilir. Bu sinapslar arasında rastgele seri aktivasyon uygulanmaz. Uzamsal mesafe aktivasyon sırasından ziyade sinyalin hedefe ulaşma gecikmesini belirler.

### 1.1. Eski branch'den korunan membran ve aksiyon potansiyeli mekanizması

`fix/synaptic-contribution-tracking` branch'indeki `Noron.py`, `Dendrid.py` ve ilgili testler incelendi. Eski mekanizmada nöronun ateşlenme kararı dendritlerden toplanan toplam etkinin membran potansiyeline uygulanması ve eşik değerine ulaşması üzerinden verilir. Bu mekanizma yeni tasarımın başlangıç referansıdır:

- Dinlenme membran potansiyeli: -70 mV.
- Ateşlenme eşiği: -55 mV.
- Depolarizasyon durumunda membran potansiyeli +30 mV yapılır.
- Sonraki durumda repolarizasyon potansiyeli -40 mV yapılır.
- Ardından hiperpolarizasyon durumunda -80 mV değerine geçilir ve 2 simülasyon adımı beklenir.
- Hiperpolarizasyon tamamlanınca nöron dinlenme durumuna ve -70 mV değerine döner.
- Dinlenme durumunda dendritlerden alınan toplam etki membran potansiyeline eklenir. Ardından potansiyel dinlenme değerine doğru sızıntı oranı kadar çekilir.
- Eski kodun varsayılan sızıntı oranı 0.05'tir.
- Pozitif ve negatif sinaptik etkiler aynı toplamda yer alır.
- Eski kodda dış duyusal girdi doğrudan membran potansiyeline etki eder ve yalnızca nöron dinlenme durumundayken uygulanır.
- Eski uygulamada nöron dinlenme dışındaki durumlarda yeni ateşlenme kararı vermez. Bu tek bir durum/refrakter döngüsüdür; mutlak ve göreli refrakter dönemlerin ayrı fizyolojik mekanizmalar olarak uygulanmış olduğu anlamına gelmez.
- Eski uygulamada ateşlenme anında katkıda bulunan bağlantılar uygunluk izi kazanır. Eski modelde ateşlenen nöronun bütün akson bağlantıları için iletim planlanırdı; bu davranış yeni tasarımda seçici çıkış sinapsı aktivasyonuyla değiştirilecektir.

+30, -40, -80 mV, iki adım ve 0.05 değerleri eski uygulamanın parametreleridir; yeni modelde biyolojik sabit sayılmaz. İlk prototipte başlangıç değerleri olarak korunabilir, sonra simülasyon zaman ölçeği ve davranış testleriyle kalibre edilir.

### 1.2. Olay zamanlaması ve ateşlenme zinciri

- Beyin olayları simülasyon zamanına göre planlar; olayların fiziksel/etkin gecikmeleri sıfırdan büyük olmalıdır. Bu, aynı anda sınırsız ve sıfır gecikmeli ateşlenme zinciri oluşmasını önler.
- Bir nöron ateşlendiğinde uygun çıkış sinapsları aynı olay anında aktive olur. Her bağlantının hedefe ulaşma zamanı bağlantı uzunluğu ve iletim hızıyla belirlenir.
- Bir hedef nörona gelen etki, kaynak nöronun ateşlenme döngüsü hâlâ sürerken hedefe ulaşır ve hedefin membran potansiyelini eşiğe taşırsa, hedef nöron kendi refrakter durumda değilse o anda ateşlenebilir. Kaynak nöronun döngüsünün bitmesi beklenmez.
- Böylece olay kuyruğu, aynı simülasyon zaman aralığında ardışık fakat gecikmeli ateşlenme zincirlerine izin verir.
- Tam aynı zaman damgasına düşen **feedback** olayları normalde bekleme/gecikme süreleri nedeniyle seyrek olmalıdır. Yine de çakışırlarsa mutlak etki büyüklüğü daha yüksek olan önce uygulanır; eşitlikte kararlı olay kimliği/sırası kullanılır. Bu bir simülasyon sıralama kuralıdır, biyolojik bir yasa değildir.
- Bir nöron refrakter durumdaysa eşik aşımı yeni aksiyon potansiyeli başlatmaz. Girdinin bekletilmesi, kaybolması veya yerel olarak sönümlenmesi henüz kesinleştirilmemiştir.

## 2. Dendritik bütünleşme ve sinapsların yerel aktivasyon potansiyeli

### 2.1. İki ayrı elektriksel düzey

Yeni tasarımda iki potansiyel birbirine karıştırılmayacaktır:

1. **Nöron membran potansiyeli (mV):** Nöronun aksiyon potansiyeli başlatıp başlatmayacağını belirler. Eski branch'deki dendrit → membran → eşik mekanizması temel alınır.
2. **Sinapsın yerel aktivasyon potansiyeli (boyutsuz, başlangıçta ortak değer):** Nöron ateşlendiği anda hangi çıkış sinapslarının aktive olabileceğini belirler. Tek başına nöronu ateşletmez.

Sinapsların yerel potansiyelleri başlangıçta aynı nötr değerden başlar. Aktivasyon eşikleri de başlangıçta ortak olabilir. Eşiklerin zamanla öğrenilip öğrenilmeyeceği şu an kesin karar değildir; mevcut tasarımda dendrit-sinaps katkısı ile sinaps aktivasyon potansiyeli ayrı parametreler olarak tutulur.

### 2.2. Dendritin yerel membran sinyali ve sinapslara dağıtılması

Kullanıcının önerisi şu şekilde somutlaştırılır: Bir dendritin topladığı pozitif veya negatif elektriksel etki, o dendritin yerel membran sinyalini oluşturur. Bu sinyal yalnızca tek bir sinapsa hapsedilmez; aynı dendritin yerel bölümündeki/ilişkili sinapslara dağıtılabilir.

- Bu dağıtım her dendrit için ayrı hesaplanır.
- İlk tasarımda bir dendritin sinyali bütün nöronun bütün sinapslarına küresel olarak yayılmaz; öncelikle o dendritle yerel/işlevsel ilişkisi bulunan sinapslara etki eder. Bu tercih yerel mimariyi korur ve gereksiz tümden-tümey ilişkileri önler.
- Dendritin membran sinyali pozitif veya negatif olabilir; işaret korunur.
- Aynı sinapsa birden fazla dendritten gelen etkiler toplamsal biçimde birikir.
- Dendritin etkisi, sinapsın yerel aktivasyon potansiyelini değiştirir. Bu yerel potansiyel, nöronun somatik membran potansiyelinin yerine geçmez ve doğrudan mV cinsinden membrana eklenmez.
- Dendritlerden toplanan işaretli etkiler eski mekanizmadaki gibi somatik membran potansiyeline katkı verir.
- Aynı dendritin yerel toplamı ayrıca normalize edilerek ilişkili sinapsların yerel aktivasyon potansiyellerine dağıtılır. Bu ikinci yol, sinapsların nöron ateşlendiğinde hangilerinin çıkış yapacağını seçer.
- Somatik membran potansiyeline katkı ile yerel sinaps potansiyeline dağıtım iki ayrı hesaplamadır. Aynı dendritik girdinin iki ayrı işlevde kullanılması modelin bilinçli tasarım tercihidir; katsayıları deneyle ayarlanmalıdır.

**Başlangıç matematiksel modeli (tasarım tercihi):**

Dendritin aldığı işaretli girdilerin yerel toplamı `s_d` olsun. İlk modelde ayrı bir dendrit membran voltajı/aktif dendrit kablosu varsaymak yerine, eski modeldeki gibi dendritte biriken pozitif ve negatif etkilerin toplamı kullanılır. Bu toplamdan sinapslara dağıtılacak boyutsuz yerel sinyal üretilir:

`u_d = tanh(s_d / S_d)`

Burada `S_d > 0` ölçek parametresidir. `u_d` [-1,+1] aralığındadır. Böylece mV ölçeğindeki dendritik toplam, boyutsuz sinaps potansiyeliyle doğrudan karıştırılmaz. Dendritin kendi başına ayrı bir membran potansiyeli taşıyan çok bölmeli biyofiziksel model olması şu an kararlaştırılmış değildir.

Dendrit `d` ile yerel ilişkisi bulunan sinaps `j` için `a_dj`, o çiftin işaretli katkı değeridir. Sinapsın o anda katkı alan ilişkili dendrit kümesi `D(j)` ise:

`Δp_j = Σ[d ∈ D(j)] (a_dj · u_d) / sqrt(max(1, |D(j)|))`

`p_j` sinapsın yerel aktivasyon potansiyelidir. `a_dj` öğrenilebilir dendrit-sinaps katkısıdır; kendi öğrenme güncellemesi toplamsal yapılır. Formülde anlık dendrit sinyaliyle çarpılması, öğrenilen `a_dj` değerinin çarpımsal öğrenme kuralıyla güncellendiği anlamına gelmez.

Karekök normalizasyonu biyolojik sabit değil, çok sayıda dendritin etkisinin kontrolsüz büyümesini önleyen başlangıç hesaplama tercihidir. Alternatif normalizasyonlar testlerle karşılaştırılabilir. Normalizasyon yalnızca o sinapsa gerçekten katkı yükleyen dendritler üzerinden yapılır.

Yerel potansiyel [-1,+1] sınırları içinde tutulur. Dendritik katkılar aynı zaman olayı için önce işaretli olarak toplamsal biçimde hesaplanır; ardından toplam etki sınırlandırılmış potansiyele uygulanır. Sinaps-sinaps aktarımı ve feedback ayrı kaynaklar olarak hesaplanır; öğrenilmiş ilişki değerleri ile geçici potansiyel değişimleri birbirine karıştırılmaz.

Herhangi bir kaynaktan gelen işaretli potansiyel artışı `δ`, mevcut yerel potansiyel `p∈[-1,+1]` için güvenli biçimde şöyle uygulanır:

`r = |δ| / (1 + |δ|)`

`δ ≥ 0: p' = p + (1 - p) · r`

`δ < 0: p' = p - (1 + p) · r`

Böylece her sonlu etki sınırlar içinde kalır. Bu dönüşüm, girdilerin kendi aralarındaki toplamsal hesabı değiştirmez; yalnızca sınırlandırılmış durum değişkenine aktarımı güvenli kılar.

### 2.3. Dendrit-sinaps katkısının öğrenilmesi

Her dendrit-sinaps çifti için ayrı bir işaretli katkı değeri bulunur. Bu değer çarpımsal bir öğrenme katsayısı gibi güncellenmez; küçük toplamsal adımlarla değişir.

- Dendrit yalnızca gerçekten potansiyel yüklediği sinaps için güncelleme alır.
- İlgili nöronun aksiyon potansiyeli sırasında sinaps aktive olursa o dendritin o sinaps üzerindeki katkısı küçük pozitif yönde güncellenir.
- Nöron ateşlenir fakat sinapsın yerel potansiyeli eşiği karşılamaz ve sinaps aktive olmazsa ilgili katkı küçük negatif yönde güncellenir.
- Dendrit o sinapsa katkı yüklememişse bu öğrenme kuralı uygulanmaz.
- Birden fazla dendritin katkısı ayrı ayrı güncellenir.
- Güncelleme büyüklüğü sinapsın yakın geçmişteki aktivitesine bağlı olabilir: yakın zamanda aktif olanlarda daha belirgin, uzun süredir aktif olmayanlarda çok küçük.
- Önceki tasarım notunda başlangıç katkılarının küçük rastgele pozitif, negatif veya sıfıra yakın değerler alması önerilmişti. Bu başlangıç dağılımı sayısal olarak kalibre edilmelidir.

Hiç ateşlenmemiş sinaps ile geçmişte ateşlenmiş fakat uzun süredir aktif olmayan sinaps aynı kabul edilmez. Hiç ateşlenmemiş sinapsa ilk değerlendirme fırsatından önce negatif öğrenme cezası verilmez. Bu, kullanıcının önceki kararlarıyla uyumlu en güvenli başlangıç kuralıdır.

### 2.4. Sinapsın aktivasyon kararı

Bir çıkış sinapsı yalnızca şu iki koşul birlikte sağlanırsa aktive olur:

1. Bağlı nöron aksiyon potansiyeli oluşturmuştur.
2. Sinapsın yerel aktivasyon potansiyeli, o sinapsın aktivasyon eşiğini karşılamıştır.

Buna göre:
- Nöron ateşlenmezse yerel potansiyeli eşik üstünde olan sinaps da aktive olmaz.
- Nöron ateşlenir fakat sinaps eşik altında kalırsa o sinaps yalnızca aktive olmaz; bunun için ek bir “başarısız ateşlenme” nesnesi veya ayrı ceza mekanizması gerekmez.
- Nöron ateşlenir ve sinaps eşik üstündeyse sinaps aktive olur ve bağlantı üzerinden sinyal/kimyasal salım sürecini başlatır.
- Aynı aksiyon potansiyelinde uygun bütün çıkış sinapsları aynı mantıksal anda aktive edilir. Rastgele sıralama kullanılmaz.
- Sinaps yerel potansiyeli zamanla nötr değere doğru sönümlenir; aksi hâlde bir kez eşiği geçen sinaps kalıcı biçimde eşik üstünde kalabilir. Başlangıç sönüm modeli `p_j(t+Δt)=p_j(t)·e^{-Δt/τ_p}` olarak seçilir. `τ_p` zaman sabitidir ve kalibrasyon parametresidir.

## 3. Sinaps-sinaps ve nöron-nöron yerel etkileşimleri

### 3.1. Aynı nörondaki sinapslar arası etkileşim

Sinaps-sinaps etkileşimleri aynı nörona ait sinapslar arasında yerel ve yönlüdür.

- Başlangıçta öğrenilmiş ilişki bulunmaz.
- Sinaps `k` aktive olduğunda öğrenilmiş `k→j` ilişkisi üzerinden aynı nörondaki `j` sinapsının yerel potansiyeline geçici etki aktarabilir.
- Kendine etki (`k=j`) yoktur.
- `k→j` ve `j→k` ayrı ilişkilerdir.
- İki sinaps birlikte aktive olursa ilgili ilişki/ilişkiler küçük pozitif yönde güçlenebilir.
- Birlikte etkinleşmeme yalnızca biri aktif, diğeri aktif değilse söz konusudur. İkisi de aktif değilse bu olaydan ilişki güncellemesi yapılmaz.
- Yönlü değerlendirmede `k` aktif, `j` aktif değilse `k→j` ilişkisi negatif yönde güncellenebilir; ters durum `j→k` için ayrı değerlendirilir.
- İlişkinin geçici potansiyel aktarımı ile kalıcı öğrenilmiş ilişki ayrı tutulur.
- İlişkiler yalnızca ilgili aktivasyon olaylarında güncellenir; bütün sinaps çiftleri her zaman adımında taranmaz.

Birlikte etkinleşmenin zaman penceresi, negatif ilişkinin alt/üst sınırları ve ilişki güncelleme miktarları kalibrasyon gerektirir.

### 3.2. Birlikte ateşlenen yerel nöronların etkileşimi

Aynı nöron içindeki sinaps-sinaps ilişkisi ile farklı nöronların birlikte ateşlenmesi ayrı mekanizmalardır.

- Kullanıcı, uzamsal olarak yerel ve zaman bakımından birlikte/çok yakın aralıkta ateşlenen nöronların birbirlerinin etkilenmesini değiştirmesini tasarım gereksinimi olarak belirtti.
- Bu etkileşim, bütün nöron çiftleri arasında yoğun ve küresel bir matris olarak kurulmayacaktır; 2B uzamsal komşuluk ve geçici etkinlik izleri üzerinden yerel adaylar bulunacaktır.
- Bu etkileşimin önceki konuşmalardaki ayrıntılı kuralı mevcut erişilebilir tasarım notlarında bulunamadı. Dolayısıyla belirli bir öğrenme formülünün daha önce kararlaştırıldığı iddia edilmemektedir.
- Şimdilik kesin olan yalnızca bu yerel nöron-nöron etkileşiminin tasarımda ayrı bir mekanizma olarak bulunmasıdır. Hangi bağlantıların/yerel potansiyellerin değişeceği, etkinliğin yönü, zaman penceresi ve tek taraflı etkinlikte ne olacağı açık karardır.

## 4. Geçici etkinlik izi

Her sinaps etkinleştiğinde geçici etkinlik izi artar ve zamanla azalır. İz:
1. Feedback'in geriye doğru hangi dallardan ilerleyebileceğini değerlendirmede,
2. Yerel etkinlik geçmişini belirlemede,
3. Sinaps-sinaps birlikte etkinleşme ilişkilerini değerlendirmede,
4. Birlikte ateşlenen yerel nöronların zaman yakınlığını belirlemede
kullanılabilir.

İz tek başına kalıcı öğrenme değildir. Deneme/episode sonunda temizlenebilir; öğrenilmiş ilişkiler ve yapısal bağlantılar bundan ayrı tutulur. Feedback için ayrıca kalıcı bir nedensel yol/iz (track) veri yapısı zorunlu değildir; geriye dönük erişim geçici izler ve güncel adım verileri üzerinden sağlanır.

İz artış miktarı, sönüm zaman sabiti ve episode sonunda hangi izlerin sıfırlanacağı kalibrasyon/deney kararıdır.

## 5. Geri bildirim ve yayılım

### 5.1. Geriye doğru dallanma

Feedback, yerel etkinlik izleri ve güncel adım verileri üzerinden geriye doğru takip edilebilen dallara yayılabilir. Her dal kendi izine göre bağımsız değerlendirilir.

- Bir dal, kendi etkinlik izi ilgili geri-adım eşiğinin altına düştüğünde durur.
- Bir dalın durması diğer dalların ilerlemesini durdurmaz.
- Sabit maksimum derinlik temel durdurma kuralı değildir; dal bazındaki iz eşiği esastır.
- Geriye doğru her adımda etkinin büyüklüğü azalır.
- Dalların iz eşiği ve adım başına azalma katsayısı kalibrasyon gerektirir.

### 5.2. Aynı hedefe ulaşan feedback olaylarının sıralanması

Feedback etkileri aynı hedefe farklı dallardan ulaşırsa birleştirilip tek toplam etki olarak uygulanmaz; her katkı ayrı ve sıralı uygulanır.

- Normal şartlarda olay zamanları arasında gecikme bulunur.
- Aynı hedef ve aynı zaman damgasında birden fazla feedback olayı çakışırsa mutlak etki büyüklüğü daha yüksek olan önce uygulanır.
- Eşit büyüklükteki olaylarda kararlı olay kimliği/sırası kullanılır.
- Her etki uygulanırken hedef potansiyelin o andaki güncel değeri kullanılır.
- Bu sıralama deterministik olmalıdır; rastgele sıralama kullanılmaz.

### 5.3. Feedback'in etki alanı ve sınırları

Feedback yalnızca ateşlenme/aktivasyon potansiyellerini küçük miktarlarda etkiler. Dendrit-sinaps öğrenilmiş katkılarını, sinaps eşiklerini veya diğer kalıcı öğrenilmiş parametreleri doğrudan değiştirmez.

- Yerel potansiyelin dış sınırları [-1,+1] olarak belirlenmiştir.
- Bu değerler yakınsama hedefi değil, aşılmaması gereken sınırlardır.
- Etki her seferinde hedefin güncel potansiyeline göre ölçeklenir.
- Sınırın matematiksel olarak aşılmasını önlemek için her tekil etki şu güvenli güncelleme biçimini kullanabilir. `p` mevcut potansiyel, `δ` işaretli feedback etkisi olsun:

`r = |δ| / (1 + |δ|)`

`δ ≥ 0: p' = p + (1 - p) · r`

`δ < 0: p' = p - (1 + p) · r`

Bu formül `p ∈ [-1,+1]` ise her sonlu `δ` için sınırların dışına çıkmaz. Her katkıdan sonra yeniden uygulanır; dolayısıyla ardışık etkiler de güvenlidir. Bu bir matematiksel sınırlandırma tercihidir, biyolojik bir denklem değildir.
- Potansiyelin hangi iç değerlere/denge noktalarına yaklaşacağı deneysel olarak belirlenir.
- Yakın zamanda ateşlenmemiş nöronlara/sinapslara etki olabildiğince minimal tutulur; hangi yerel iz ve zaman ölçeğinin kullanılacağı kalibrasyon gerektirir.

## 6. Nörotransmitterler, kimyasal sinyaller ve mikroglia-benzeri yapılar

### 6.1. Bir sinapsın birden fazla nörotransmitter salabilmesi

Bir nöronun birden fazla nörotransmitter kullanabilmesi biyolojik olarak gerçektir. Daha da önemlisi, farklı transmitterler aynı nöronun farklı terminallerinden veya aynı terminaldeki farklı vezikül havuzlarından salınabilir; bazı örneklerde birden fazla transmitter aynı vezikülde birlikte paketlenip salınabilir. Dolayısıyla tek bir sinaps/terminalin birden fazla transmitter türünü desteklemesi biyolojik açıdan mümkündür; ancak bütün sinapsların her transmitter türünü birlikte saldığı varsayılmayacaktır.

Önceki konuşmalarda bu kavramın temel temsili açıkça tartışılmıştı: `Q_k(x,t)`, k türü nörotransmitterin x konumundaki, t anındaki yerel kimyasal yoğunluğu/etkinliğidir; `R_{ik}` ise i dendritinin k transmitterine karşı işaretli reseptör duyarlılığıdır. Kimyasal sinyalin etkisi, sinaptik elektriksel potansiyelden ayrı bir alandır ve hacimsel iletimle sinaptik boşluk dışında da yayılabilir. Bu önceki kavram korunur. Önceki konuşmada bu alanın tam sayısal güncelleme denklemi kesinleştirilmemişti; aşağıdaki denklem yeni tasarım tercihi olarak önerilir:

`∂Q_k/∂t = D_k ∇²Q_k - λ_k Q_k + S_k(x,t)`

Burada `D_k` yayılım katsayısı, `λ_k` temizlenme/sönüm oranı, `S_k` sinaps/terminal salımlarından gelen kaynak terimidir. 2B simülasyonda bu denklem sürekli uzayda çözülmek zorunda değildir; yerel komşulara sınırlı aktarım ve zamanla azalma biçiminde ayrıklaştırılabilir. Bu, hacimsel iletimi temsil eden hesaplama modelidir; tüm kimyasal türlerin beyinde aynı hızda yayıldığı iddia edilmez.

Bir dendritin k transmitterini algılama yanıtı için başlangıçta:

`h_i = Σ_k R_{ik} · f_k(Q_k(x_i,t))`

kullanılabilir. Başlangıçta sınırlı reseptör yanıtı için `f_k(Q)=Q/(K_k+Q)` seçilebilir; `K_k>0` yarı-doyum parametresidir. `R_{ik}` pozitif, negatif veya sıfır olabilir: aynı transmitter bir dendritte kolaylaştırıcı, diğerinde baskılayıcı veya etkisiz olabilir. Bu, reseptör yanıtının basit bir simülasyon yaklaşımıdır; bütün reseptörlerin biyolojik olarak bu tek eğriyi izlediği iddia edilmez. Bu kimyasal yanıt, dendritin elektriksel toplamından ve dendrit-sinaps öğrenilmiş katkısından ayrı tutulur; hangi yerel işlem üzerinden bunları modüle edeceği aşağıda tanımlanır.

- Her sinaps/akson terminali, desteklediği transmitter türleri için ayrı salım profilleri taşır. Önceki konuşmalarda bir sinapsın aynı ateşlenme olayında birden fazla transmitter salgılayabilmesi açıkça kabul edilmişti; bu karar korunur.
- Bir ateşlenme olayı birden fazla transmitter türünün birlikte salınmasına yol açabilir. Türlerin salım miktarları ayrı hesaplanır; her türün aynı miktarda veya her olayda zorunlu olarak salınması gerekmez.
- Bir sinaps/terminalin birden fazla transmitter türünü desteklemesi, bunların aynı vezikülde paketlenmesini zorunlu kılmaz. Ayrı vezikül havuzları ve bazı biyolojik sistemlerde birlikte paketlenme farklı olasılıklardır.
- Salım, nöronun aksiyon potansiyeli ve sinapsın aktive olmasıyla tetiklenebilir. Dendritten gelen elektriksel sinyal ve terminalin kimyasal/modülatör durumu, o terminalin hangi transmitter profillerini ne miktarda salacağını belirler.
- Dendritik sinyal, terminalde bulunmayan bir transmitter türünü aniden yaratmaz. Salınabilecek türler terminalin mevcut repertuvarıyla sınırlıdır.
- Salım olayı kimyasal alan `Q_k(x,t)`'ye kaynak ekler. Alan yerel hacimsel iletimle yayılır ve zamanla temizlenir. Birden fazla transmitter alanı aynı anda bulunabilir.

Bu, kullanıcının “hangi transmitterin salgılanacağı dendritten gelen sinyale göre değişsin” kararını koruyan, fakat terminalin yalnızca sahip olduğu transmitter repertuvarını salabileceği ilkesini de gözeten soyutlamadır. Dendritin kendisinin her durumda klasik nörotransmitter salgıladığı varsayılmaz; dendritik sinyal, ilgili çıkış terminalinin salım profilini düzenler.

Önceki konuşmalarda ayrıca temel transmitter + aktiviteye bağlı ek transmitter profili fikri önerilmişti. Bunun kullanıcı tarafından kesinleştirilmiş bir kural olduğu doğrulanamadı; bu nedenle seçenek olarak kalır, zorunlu mimari kural yapılmaz.

### 6.2. Dendritlerin transmitterleri algılaması

Her dendritin transmitter türlerine karşı reseptör-benzeri duyarlılık profili bulunur.

- Aynı transmitter farklı dendritlerde farklı etki oluşturabilir; bu, `R_{ik}` reseptör duyarlılık işareti ve büyüklüğüyle temsil edilir.
- Dendritin algıladığı kimyasal bileşim, dendritin sinapslara yüklediği katkının yönünü ve büyüklüğünü değiştirebilir.
- Presinaptik salım etkisi ile postsinaptik/dendritik algılama etkisi ayrıdır: transmitterin salındığı terminalde salım olasılığı, miktarı veya sonraki salım profili değişebilir; aynı transmitter başka bir dendrit tarafından algılandığında o dendritin yerel elektriksel katkısı veya plastisite davranışı değişebilir. Bunlar tek bir “transmitter etkisi” parametresine indirgenmez.
- Bir transmitter dendrit-sinaps katkısını güçlendirebilir; başka bir transmitter zayıflatabilir.
- Ayrı bir modülatör sinyal, dendritin mevcut katkı profilini yeniden düzenleyebilir. Kullanıcının “etkileri baştan yazma” örneği için önerilen güvenli uygulama, yalnızca o dendritin yerel katkılarını kontrollü bir yeniden-kurulum/baseline'a çekme ve sonrasında yeniden öğrenmeye izin verme işlemidir; ağın tüm katkılarını küresel olarak silmez.
- Bazı kimyasal sinyaller bağlantısız bir akson terminalinin uygun dendrit aramasını/bağlantı oluşumunu kolaylaştırabilir.
- Bazıları mevcut zayıf bağlantıyı koruyabilir veya yapısal onarım/stabilizasyon sürecini destekleyebilir.
- Bazıları çalışmayan/zayıf bağlantıyı budanmaya aday hâle getirebilir; bazıları aktif bağlantıyı da düzenleyebilir. Etkinlik durumu tek başına mutlak koruma veya mutlak kopma garantisi değildir; reseptör profili, kullanım geçmişi ve yerel kimyasal bileşim birlikte değerlendirilir.
- Bu nedenle transmitter etkileri yalnızca “aktif sinapsı güçlendir / pasif sinapsı sil” gibi iki kutuplu kurala indirgenmez.

Bir transmitterin etkisi yalnızca transmitter adından çıkarılmaz. Dendritin reseptör profili, transmitter yoğunluğu ve sinyalin zamanlaması birlikte belirleyicidir. Aynı transmitterin her hedefte zorunlu olarak uyarıcı veya baskılayıcı olduğu varsayılmaz.

### 6.3. Kimyasal sinyal sınıfları

İlk modelde çok sayıda gerçek molekülü ayrı ayrı simüle etmek yerine işlevsel sınıflar kullanılacaktır. Bunlar gerçek biyolojide birebir aynı molekül değildir; soyutlama sınıflarıdır:

1. **Hızlı sinaptik iletim sinyalleri:** Hedef membran/dendrit potansiyelini hızlı biçimde etkileyen uyarıcı veya baskılayıcı etkiler.
2. **Modülatör sinyaller:** Dendrit reseptör duyarlılığını, transmitter salım miktarını/olasılığını ve plastisite hassasiyetini değiştiren sinyaller.
3. **Büyüme ve stabilizasyon sinyalleri:** Bağlantının korunmasını, zayıf bağlantının güçlenmesini veya yeni bağlantının olgunlaşmasını destekleyen sinyaller.
4. **Budama/hasar işaretleri:** Bağlantının zayıf, gereksiz veya ortadan kaldırılmaya aday olduğunu yerel mikroglia-benzeri yapılara bildiren sinyaller.

Son iki sınıfın tamamı klasik nörotransmitter değildir. Nörotrofik faktörler, purinerjik sinyaller, sitokinler ve kompleman benzeri işaretler ayrı kimyasal sinyal aileleri olarak modellenebilir. Bunlar `Q_k) benzeri ayrı kimyasal alanlar olarak soyutlanabilir ancak biyolojik sınıflandırmada klasik nörotransmitter diye adlandırılmamalıdır.

### 6.4. Bağımsız mikroglia ajanları ve yerel denetim

Mikroglia-benzeri yapılar bağlantı nesnesinin içine gömülmez; 2B uzayda kendi konumu ve algılama alanı bulunan bağımsız ajanlardır. İlk simülasyon soyutlamasında hücre gövdesi sabittir; algılama yarıçapı hareketli uzantıların yerel çevreyi taramasını temsil eder.

- Her bağlantı kullanım izini, yapısal bütünlüğünü ve bakım parametrelerini kendi üzerinde taşır.
- Mikroglia, uzamsal indeksin bulduğu yakın bağlantı adaylarını değerlendirir. Uzamsal indeks yalnızca adayları bulur; koruma, zayıflatma veya koparma kararı vermez.
- Değerlendirme; kullanım izi, bağlantının yapısal bütünlüğü ve yerel büyüme/stabilizasyon/budama kimyasal alanlarının birlikte etkisine dayanır.
- Kullanılmama tek başına fiziksel kopma nedeni değildir. İlk modelde budama işareti, düşük kullanım ve yeterince azalmış yapısal bütünlük birlikte aranır.
- Mikroglia yapısal bakım kararını verir. Beyin yalnızca bakım olayını zamanlar ve mikroglianın kopardığı bağlantıyı ağ kayıtlarından temizler; hangi bağlantının değişeceğini seçmez.
- Dendrit reseptörlerinin transmitter yanıtı ile mikroglianın yapısal sinyal yanıtı ayrı yerel mekanizmalardır. Aynı kimyasal alanı farklı duyarlılıklarla yorumlayabilirler.
- İşlevsel zayıflama ile fiziksel eliminasyon ayrı süreçlerdir.
- Tekrarlanan bakım açıkça başlatılır; `bakim_araligi` sonraki değerlendirme zamanını belirler. Döngü yalnızca `Beyin.calistir(son_zaman=...)` ile verilen sonlu simülasyon aralığında ilerler; sınırsız çalıştırmada sonsuz olay zinciri oluşturulmaz.

Bu yaklaşım, mikroglianın bağımsız bir hücresel aktör olmasını korurken simülasyonu basit tutar. Gerçek hücre göçü, dallanan uzantı geometrisi, fagositoz biyokimyası ve ayrıntılı moleküler repertuvar bu aşamada modellenmez.

## 7. Bağlantıların yaşlanması, korunması, kopması ve yeniden oluşması

### 7.1. Bağlantı durumu

Her bağlantı en azından şu bilgileri taşımalıdır:
- işlevsel iletim gücü,
- yapısal bütünlük/dayanıklılık,
- son kullanım zamanı ve kullanılmama geçmişi,
- geçici etkinlik izi veya kullanım geçmişi,
- koruma/stabilizasyon ve budama işaretlerinin yerel düzeyleri,
- bağlı olduğu akson terminali ve dendrit.

İşlevsel gücün azalması bağlantının fiziksel olarak yok olduğu anlamına gelmez. Yapısal bütünlük yeterince düşmeden bağlantı silinmez.

### 7.2. Yaşlanma ve eliminasyon

- Kullanılmayan bağlantılar zamanla yaşlanabilir; tek bir kullanılmama olayında silinmez.
- Kullanım, bağlantının korunmasını destekler ve kullanılmama geçmişini azaltabilir.
- Yalnızca kullanılmama sayacı bağlantıyı silmek için yeterli değildir.
- Eliminasyon için uzun süreli düşük kullanım/zayıflık ile yerel budama işaretlerinin birlikte bulunması gerekir.
- Koruma veya onarım sinyalleri budama baskısını azaltabilir.
- Bağımsız mikroglia ajanı, uygun budama koşulları devam ederse bağlantının yapısal bütünlüğünü azaltabilir ve eşik koşulları sağlandığında fiziksel olarak kaldırabilir.
- Bağlantı kopma kararı merkezi Beyin tarafından veya bağlantı nesnesinin kendi başına verilmez; bağımsız mikroglia ajanı yerel koşulları değerlendirir.
- Önceki taslaktaki 1.0 dayanıklılık, 0.9995 kullanılmama çarpanı ve 0.1 kopma sınırı yalnızca örnekti; kesin parametre değildir ve bu tasarımda zorunlu tutulmaz.

### 7.3. Yeni bağlantı oluşumu ve eski bağlantının onarımı

İki olay birbirinden ayrılır:

**Mevcut fakat zayıflamış bağlantının onarımı/stabilizasyonu**
- Bağlantı fiziksel olarak hâlâ mevcutsa uygun büyüme/stabilizasyon sinyalleri onun yapısal bütünlüğünü ve dayanıklılığını artırabilir.
- Onarım, bağlantıyı tek adımda eski gücüne döndürmek zorunda değildir; kademeli olabilir.
- Kullanım ve uygun kimyasal sinyaller olgunlaşmayı destekleyebilir.

**Kopmuş bağlantının yeniden kurulması**
- Fiziksel olarak kopmuş bağlantı artık onarılabilir bir mevcut bağlantı sayılmaz.
- Bağlantısız akson terminali 2B uzamsal aramayla uygun/boş dendrit adayı bulur.
- Yerel bağlantı-oluşum sinyali ve terminalin aktivasyon/arama koşulu yeni bağlantı oluşumunu destekleyebilir.
- Yeni bağlantı başlangıçta zayıf ve kararsız olur; kullanımla ve stabilizasyon sinyalleriyle olgunlaşır.
- Rastgele tüm ağdan hedef seçilmez; yerel adaylar arasından seçim yapılır.

### 7.4. Bağlantılarını kaybeden nöronun toparlanması

- Tek bir bağlantının kaybı, bütün nöronun otomatik olarak varsayılan duruma sıfırlanmasını tetiklemez.
- Nöronun kullanılabilir bütün çıkış bağlantılarını kaybetmesi, toparlanma modunu başlatır.
- Toparlanma modunda yerel bağlantı-oluşum sinyallerine duyarlılık geçici olarak artar ve ateşlenme/aktivasyon hazırlığı varsayılan nötr seviyeye döndürülür.
- Bu pozitif toparlanma etkisi sınırsız veya kalıcı değildir. Yeni bağlantı oluşup kullanılabilir hâle geldiğinde veya belirli bir toparlanma süresi dolduğunda normal duruma döner.
- Yeni bağlantı kurulduktan sonra kısa bir olgunlaşma/stabilizasyon dönemi olabilir; ancak toparlanma bias'ı sonsuza kadar sürmez.

Bu, tek bağlantı kaybında gereksiz küresel reset yapılmasını engeller ve tamamen bağlantısız nörona yeniden ağ kurma fırsatı verir.

## 8. Uzamsal temsil ve hesaplama

- Uzamsal temsil **2B** olacaktır; kullanıcı bunun daha önce kararlaştırıldığını belirtti.
- Nöron, dendrit, akson terminali, bağlantılar ve mikroglia ajanları 2B koordinatlarla temsil edilir. Mikroglia kendi konumundan yerel algılama yarıçapı içinde bağlantıları tarar.
- Basit koordinat çiftleri `(x, y)` kullanılır. Gereksiz vektör soyutlamaları eklenmez.
- Yerel komşuluk ve arama yarıçapı karşılaştırmalarında karekök almadan `d²=(x1-x2)²+(y1-y2)²` kullanılır.
- Gerçek iletim gecikmesi için fiziksel mesafe gerekiyorsa karekök yalnızca bu aşamada hesaplanabilir.
- Bağlantı uzunluğu, sinyalin hedefe ulaşma gecikmesini etkiler. Başlangıçta düz çizgi mesafesi yaklaşık iletim yolu olarak kullanılabilir; aksonun kıvrımlı geometrisi ilk modelde zorunlu değildir.
- Yerel arama yarıçapı ve iletim hızı sayısal olarak kalibre edilecektir.
- Yerel bağlantı adaylarını tüm ağı taramadan bulmak için ilk prototipte hücre tabanlı 2B uzamsal indeks kullanılır; indeks karar vermez, yalnızca yakın adayları döndürür.
- Sinaps-sinaps ve nöron-nöron ilişkileri seyrek tutulur; yalnızca öğrenilmiş/aktif ilişkiler saklanır.

## 9. Başlangıç parametreleri ve matematiksel kalibrasyon

Aşağıdakiler prototipte kalibre edilecek parametrelerdir; biyolojik sabit olarak sunulmaz:

- Eski branch'den başlangıç membran değerleri: -70 mV dinlenme, -55 mV eşik, +30 mV depolarizasyon, -40 mV repolarizasyon, -80 mV hiperpolarizasyon, 2 adım hiperpolarizasyon, 0.05 sızıntı.
- Yerel sinaps potansiyeli başlangıcı: bütün sinapslarda aynı nötr değer (önerilen 0).
- Yerel sinaps aktivasyon eşiği: başlangıçta bütün sinapslarda aynı; sayısal değer deneyle belirlenecek. Eski 0.2–0.4 önerisi doğrulanmış karar değildir.
- Yerel sinaps potansiyelinin sönüm zaman sabiti `τ_p`: deneysel.
- Transmitter reseptör yanıtının yarı-doyum parametresi `K_k`: deneysel.
- Dendrit yerel sinyal ölçeği `S_d`: deneysel.
- Dendrit-sinaps katkılarının başlangıç dağılımı: küçük, işaretli ve sınırlandırılmış; pozitif/negatif/sıfıra yakın örnekler.
- Dendrit-sinaps katkı güncelleme miktarları: deneysel.
- Dendrit normalizasyonunun karekök biçimi: ilk prototip tercihi; alternatiflerle test edilebilir.
- Sinaps-sinaps ilişki zaman penceresi, güncelleme adımı ve sınırları: deneysel.
- Yerel nöron-nöron birlikte ateşlenme penceresi ve etkisi: henüz tanımlanmadı.
- Etkinlik izi artış/sönüm değerleri: deneysel.
- Feedback dallanma eşiği ve adım başına azalma: deneysel.
- Feedback potansiyel sınırlandırması: yukarıdaki güvenli formül başlangıç tercihi.
- Her transmitter türü için terminal repertuvarı, salım profili, `Q_k(x,t)` yayılım/sönüm parametreleri ve dendrit duyarlılığı `R_{ik}`: deneysel.
- Hacimsel kimyasal iletimin yerel arama/ızgara çözünürlüğü ve komşulara aktarım katsayıları: deneysel.
- Kimyasal sinyal sınıflarının yerel etki yarıçapı ve sönüm hızları: deneysel.
- Mikroglia ajanlarının bakım zaman ölçeği, algılama yarıçapı ve budama/koruma tepkileri: deneysel.
- Bağlantı yaşlanması, yapısal bütünlük ve eliminasyon koşulları: deneysel.
- Bağlantı oluşum yarıçapı, yeni bağlantı başlangıç gücü ve olgunlaşma koşulları: deneysel.
- İletim hızı ve minimum pozitif olay gecikmesi: deneysel.

## 10. Zorunlu testler

1. Membran potansiyeli eşik altında kaldığında nöron ateşlenmez; eşik değerine ulaştığında ateşlenir.
2. Pozitif ve negatif dendritik/sinaptik etkiler membran potansiyelini doğru yönde değiştirir.
3. Eski membran sızıntısı ve depolarizasyon/repolarizasyon/hiperpolarizasyon döngüsü doğru uygulanır.
4. Refrakter durumdayken yeni aksiyon potansiyeli başlatılmaz.
5. Sinaps yerel potansiyeli eşik üstünde olsa bile nöron ateşlenmeden sinaps aktive olmaz.
6. Nöron ateşlendiğinde yalnızca yerel eşik koşulunu sağlayan çıkış sinapsları aktive olur.
7. Uygun çıkış sinapsları aynı ateşlenme olayında aktive edilir; rastgele seri sıra sonucu değiştirmez.
8. Dendritin yerel sinyali yalnızca o dendritle ilişkili yerel sinapsları etkiler.
9. Pozitif/negatif dendrit sinyali yerel sinaps potansiyelinde işaretini korur.
10. Bir sinapsa katkı yükleyen birden fazla dendritin etkisi toplamsal hesaplanır ve normalizasyon sınanır.
11. Dendrit katkısı yüklemeyen dendrit-sinaps çifti öğrenme güncellemesi almaz.
12. Aktive olan sinaps için katkı pozitif; ateşlenme fırsatında aktive olmayan fakat katkı almış sinaps için katkı negatif yönde küçük güncellenir.
13. Hiç ateşlenmemiş sinaps, geçmişte ateşlenip uzun süredir aktif olmayan sinapstan farklı davranır.
14. Yerel sinaps potansiyeli zamanla nötr değere sönümlenir.
15. Sinaps-sinaps etkileşimi yönlüdür; `k→j` ile `j→k` bağımsız davranır.
16. İki sinaps da etkin değilse birlikte etkinleşmeme güncellemesi yapılmaz.
17. Yalnızca biri etkinse etkin→etkin olmayan yönlü ilişki için negatif güncelleme kuralı çalışır.
18. Birlikte etkinleşmede ilişki güçlenmesi geçici potansiyel aktarımından ayrı test edilir.
19. Yerel nöron-nöron birlikte ateşlenme mekanizması tanımlandığında uzamsal ve zamansal komşuluk testleri eklenir.
20. Feedback dalları birbirinden bağımsız ilerler; bir dalın durması diğerini durdurmaz.
21. Aynı hedefe aynı anda gelen feedback olayları mutlak etki büyüklüğüne göre sıralanır.
22. Feedback'in her tekil ve ardışık etkisinde potansiyel [-1,+1] aralığında kalır.
23. Feedback'in her geriye adımda zayıflaması doğrulanır.
24. Bir sinaps/terminal aynı ateşlenme olayında desteklediği birden fazla transmitter türünü ayrı miktarlarda salabilir.
25. Dendritin reseptör profili, aynı transmitterin farklı dendritlerde farklı etkiler oluşturmasını sağlar.
26. Her transmitter türünün `Q_k(x,t)` kimyasal alanı diğer türlerden ayrı tutulur; eşzamanlı salımlar birbirinin yoğunluk kaydını ezmez.
27. `Q_k(x,t)` salım noktasından yayılır, uzaklıkla etkisi azalır ve zamanla temizlenir.
28. Dendritin `R_{ik}` duyarlılığı pozitif, negatif veya sıfır olduğunda beklenen kolaylaştırıcı, baskılayıcı veya etkisiz yanıt oluşur.
29. Aynı transmitter farklı dendritlerde farklı yanıt oluşturabilir.
30. Presinaptik salım modülasyonu ile postsinaptik/dendritik algılama etkisi birbirinden ayrı test edilir.
31. Yerel yeniden düzenleme sinyali yalnızca hedef dendritin/bağlantı alanının katkılarını etkiler; küresel öğrenilmiş parametreleri sıfırlamaz.
32. Mikroglia-benzeri denetim bağımsız 2B ajanlar tarafından yürütülür; uzamsal indeks yalnızca yerel adayları bulur, merkezi Beyin budama kararı vermez.
33. Bağlantının işlevsel zayıflaması ile fiziksel kopması ayrı olaylardır.
34. Yalnızca kullanılmama süresi tek başına bağlantıyı silmez.
35. Koruma/stabilizasyon sinyali bağlantının yaşlanmasını veya budama baskısını azaltabilir.
36. Bağlantısız terminal, 2B yerel aramayla uygun dendrit adayı bulabilir.
37. Yeni bağlantı zayıf başlar ve kullanım/stabilizasyonla olgunlaşır.
38. Zayıf ama mevcut bağlantı onarılabilir; kopmuş bağlantı yeni bağlantı oluşumu gerektirir.
39. Nöron yalnızca bütün kullanılabilir çıkış bağlantılarını kaybettiğinde toparlanma moduna girer.
40. Olay gecikmeleri sıfırdan büyüktür; kaynak nöronun ateşlenme döngüsü sürerken hedef nöronun eşik aşımıyla ateşlenmesi mümkündür.
41. Aynı seed ve aynı başlangıç koşulları tekrarlanabilir sonuç verir.

## 11. Açık araştırma ve karar noktaları

- “Dendritin ilişkili sinapsları” ile nöronun çıkış akson terminallerindeki sinapsların topolojik eşlemesi nasıl kurulacak? Biyolojik olarak dendritler postsinaptik girdileri alırken çıkış terminalleri akson üzerindedir; simülasyonda dendritik sinyalin hangi çıkış sinapslarını hazırladığı açıkça tanımlanmalıdır.
- Dendritin yerel sinyalinin hangi sinapslarla ilişkili olacağı mevcut topoloji üzerinden mi, uzamsal yakınlık üzerinden mi belirlenecek?
- Dendrit-sinaps katkısı `a_dj` için kesin başlangıç aralığı ve güncelleme miktarı ne olacak?
- Dendritik sinyal ölçeği `S_d` nasıl kalibre edilecek?
- Yerel sinaps aktivasyon eşiği zamanla öğrenilecek mi, yoksa sabit mi kalacak?
- Refrakter dönemde gelen sinaptik etkiler bekletilecek mi, sönümlenecek mi, yoksa bir kısmı mı korunacak?
- Yerel nöron-nöron birlikte ateşlenme etkileşimi tam olarak hangi parametreleri değiştirecek? Önceki konuşmanın ayrıntılı formülü mevcut notlarda bulunmadığından uydurulmamıştır.
- Sinaps-sinaps birlikte etkinleşme zaman penceresi ve negatif güncelleme miktarı ne olacak?
- Feedback'in zaman gecikmesi ve dal sönüm katsayısı ne olacak?
- Önceki konuşmada tanımlanan `Q_k(x,t)` kimyasal yoğunluk alanının ayrık 2B yayılım/sönüm katsayıları nasıl kalibre edilecek?
- Terminalin transmitter repertuvarı ve dendritten gelen sinyalin çoklu salım profilini nasıl değiştirdiği nasıl kalibre edilecek?
- Dendrit reseptör duyarlılığı `R_{ik}` zamanla öğrenilecek mi, sabit mi kalacak?
- Dendritin kimyasal sinyale yanıtı mevcut `a_{dj}` katkılarını hangi koşullarda modüle edecek, yeniden düzenleyecek veya kontrollü biçimde baştan kuracak?
- İlk prototipte kaç işlevsel kimyasal sinyal sınıfı kullanılacak?
- Bağlantı nesnesinin mikroglia-benzeri yerel denetim durumları, bakım sıklığı ve kimyasal sinyal yanıtları nasıl kalibre edilecek?
- Bağlantı eliminasyonunda budama işaretinin ne kadar süre devam etmesi gerekecek?
- Bağlantı oluşumu için terminal aktivasyon girişimi ve kimyasal sinyalin birlikte mi, alternatif koşullar olarak mı aranacağı kesinleştirilecek.
- Yeni bağlantı olgunlaşma süresi ve bağlantısız nöronun toparlanma süresi ne olacak?
- İletim hızı, minimum gecikme ve aksiyon potansiyeli süresi hangi simülasyon zaman birimleriyle ifade edilecek?

## 12. Biyolojik dayanaklar ve modelleme sınırları

Aşağıdaki bulgular tasarımın biyolojik esinini destekler; simülasyondaki her matematiksel kuralın biyolojik olarak birebir bulunduğunu göstermez.

- Dendritik sinaptik girdiler uzamsal ve zamansal olarak bütünleşir; bu bütünleşmenin sonucu membran potansiyelini ve aksiyon potansiyeli çıktısını etkiler. Dendrit morfolojisi, aktif membran özellikleri ve sinaps konumu bu entegrasyonu değiştirebilir. Kaynak: Magee, *Dendritic integration of excitatory synaptic input* (2000), https://www.nature.com/articles/35044552
- Birçok nöron birden fazla transmitter kullanabilir. Birden fazla transmitter farklı vezikül havuzlarında bulunup ayrı zamanlarda salınabilir; bazı sistemlerde aynı vezikülde birlikte paketlenmeleri de gösterilmiştir. Bu nedenle çoklu transmitter desteği biyolojik olarak temellidir; bütün sinapsların aynı transmitter kombinasyonunu saldığı varsayımı doğru değildir. Kaynak: Wallace & Sabatini, *Synaptic and circuit functions of multitransmitter neurons in the mammalian brain* (2023), https://pmc.ncbi.nlm.nih.gov/articles/PMC10592565/
- Hacimsel iletim, transmitterlerin klasik sinaptik temas noktalarına bağlı kalmadan hücre dışı ortamda yayılıp yakındaki reseptörleri etkilemesine imkân verir. Yayılım, geri alım, yıkım ve reseptörlerin konumu sinyalin uzamsal-zamansal profilini belirler. Bu nedenle `Q_k(x,t)) alanı biyolojik esin taşır; ancak tek bir ortak yayılım katsayısı bütün transmitterler için doğru kabul edilmez. Kaynak: Özçete, Banerjee & Kaeser, *Mechanisms of neuromodulatory volume transmission* (2024), https://pmc.ncbi.nlm.nih.gov/articles/PMC11540752/
- Sinaptik vezikül salımı aksiyon potansiyeliyle terminale ulaşan elektriksel aktivite ve kalsiyum aracılı süreçlerle tetiklenir; salım olasılığı ve miktarı yerel olarak düzenlenebilir. Kaynak: Branco & Staras, *The probability of neurotransmitter release* (2009), https://www.nature.com/articles/nrn2634
- Mikroglia nöral aktiviteyi algılayabilir ve sinapsların oluşumu, korunması, işlevsel düzenlenmesi ve eliminasyonuna katılabilir. Ancak sinaps eliminasyonunun hücresel ayrıntıları ve bağlama göre değişimi hâlâ araştırılmaktadır. Kaynak: *Microglia: Activity-dependent regulators of neural circuits* (2024), https://pubmed.ncbi.nlm.nih.gov/38294960/ ; Pereira-Iglesias et al., *Microglia as hunters or gatherers of brain synapses* (2025), https://www.nature.com/articles/s41593-024-01818-w
- Biyolojik mikroglia, sinapsların oluşumu, korunması ve budanmasında yer alır; BrainNew'de bu davranış bağlantı nesnesine ait yerel bakım/budama kurallarıyla soyutlanır. Bu yazılım temsili gerçek mikroglia hücresinin yapısal konumunu birebir modellemez. Özellikle kopmuş bir bağlantının doğrudan “tamiri” ile yeni sinaps oluşumu aynı biyolojik olay gibi ele alınmamalıdır.

## 13. Performans ve davranışı koruyan optimizasyon ilkeleri

Bu bölümdeki optimizasyon kararları kullanıcı tarafından onaylanmıştır. Amaç yalnızca daha hızlı çalışan bir simülasyon elde etmek değildir: **öğrenme kuralları, sinyal akışı, olay zamanlaması ve yerel etkileşimlerin anlamı korunurken gereksiz hesaplama ve bellek maliyeti azaltılacaktır.** Optimizasyon, modelin davranışını değiştirmek için gerekçe olarak kullanılamaz.

### 13.1. Değişmez öncelik

Optimizasyon yapılırken öncelik sırası şöyledir:

1. Sistemin mantıksal ve sayısal doğruluğu.
2. Öğrenme ve etkileşim davranışının korunması.
3. Aynı başlangıç koşulları ve aynı rastgelelik tohumu altında tekrarlanabilirlik.
4. Performans ve bellek verimliliği.
5. Gereksiz mimari karmaşıklıktan kaçınma.

Bir optimizasyon bu koşulları ihlal ediyorsa kabul edilmez. Özellikle hesaplama azaltmak amacıyla öğrenme güncellemeleri atlanmaz, olaylar gelişigüzel birleştirilmez, kimyasal etki yarıçapı veya zaman pencereleri keyfî biçimde daraltılmaz ve yerel etkileşimler küresel/merkezi bir kurala dönüştürülmez.

### 13.2. Onaylanan hesaplama stratejileri

- **Olay-tabanlı hesaplama:** Bir bileşen yalnızca kendisini etkileyen bir olay gerçekleştiğinde veya zamanlanmış bir değerlendirme zamanı geldiğinde işlenir. Bütün nöronlar, sinapslar, dendritler ve bağlantılar her simülasyon adımında koşulsuz taranmaz.
- **Seyrek ilişkiler:** Dendrit-sinaps ve sinaps-sinaps ilişkileri yalnızca gerçekten tanımlanmış/öğrenilmiş ilişkiler için saklanır. Bütün olası çiftler için yoğun matris oluşturulmaz. Bir ilişkinin bulunmaması, tasarımda başlangıç ilişkisinin bulunmaması anlamına gelir; bu durum kendiliğinden yeni bir etki veya öğrenme kuralı üretmez.
- **Yerel kimyasal yayılım:** Kimyasal sinyal yalnızca salımın etkileyebileceği yerel uzamsal bölge ve ilgili zaman aralığında hesaplanır. Bütün 2B uzayın her transmitter türü için her zaman adımında taranması temel yöntem değildir. Yerel yayılım yaklaşımı, seçilen kimyasal yayılım/sönüm modelinin etkisini korumalıdır; etki alanını yalnızca performans uğruna değiştirmek kabul edilmez.
- **Gecikmeli/lazy potansiyel güncellemesi:** Zamanla nötr değere sönümlenen potansiyeller, her zaman adımında fiziksel olarak güncellenmek yerine son güncelleme zamanı saklanarak ihtiyaç anında hesaplanabilir. Hesaplanan değer, aradaki bütün zamanın sönümünü uygulamış olmalı ve her olayın göreceği değer adım-adım güncellemeyle matematiksel olarak eşdeğer olmalıdır. Bu yöntem zamanın veya sönümün atlanması anlamına gelmez.
- **Hedefe göre olay gruplama:** Olaylar hedef bileşene göre gruplanabilir. Ancak aynı hedefe ulaşan feedback katkıları mevcut tasarımda tanımlanan ayrı ve sıralı uygulama kuralını korur; katkılar davranışı değiştirecek biçimde tek bir toplama indirgenmez. Aynı zaman damgasındaki çakışmalarda belirlenmiş büyüklük ve kararlı eşitlik sırası korunur.
- **Uzamsal indeksleme gerektiğinde:** 2B koordinatlar ve kare uzaklık kontrolleri temel kalır. Aday arama maliyeti ölçümlerde sorun oluşturursa grid, spatial hash veya benzeri bir indeks eklenebilir. İndeks yalnızca adayları daha hızlı bulur; gerçek uzaklık/komşuluk koşulunun yerine geçmez ve adayları sessizce dışarıda bırakmaz.
- **Sabit hesapların yeniden kullanılması:** Değişmeyen normalizasyon değerleri, katsayılar ve benzeri hesaplar uygun olduğunda önceden hesaplanabilir veya önbelleğe alınabilir. Önbellek, parametre değiştiğinde geçersiz kılınmalı; eski değer kullanımı davranışı değiştirmemelidir.

### 13.3. Matematiksel ve davranışsal eşdeğerlik şartı

- Bir optimizasyonun kabulü yalnızca daha az işlem yaptığına bakılarak verilmez. Referans, daha basit/doğrudan hesaplama biçimiyle karşılaştırmalı doğrulamadır.
- Lazy sönüm, olay zamanlaması, kimyasal yayılım, yerel potansiyel sınırlandırması ve öğrenme güncellemeleri için karşılaştırmalı testler yazılır.
- Olayların sıralı uygulanmasının sonucu etkilediği mekanizmalarda olay sırası korunur. Paralelleştirme veya toplu hesaplama, bu sırayı değiştirecekse doğrudan uygulanmaz.
- Aynı seed ve başlangıç koşullarıyla deterministik sonuç üretme şartı korunur. Paralel hesaplama kullanılırsa sonuçların gelişigüzel tamamlanma sırasına bağlı olmasına izin verilmez.
- Kayan nokta toplama sırası değişebileceğinden, matematiksel olarak eşdeğer görünen yeniden sıralamalar dahi davranış testleriyle doğrulanır. Öğrenme dinamiklerinde anlamlı fark yaratıyorsa kullanılmaz.
- Yaklaşık hesaplama, kesme eşiği, örnekleme veya çözünürlük azaltma gibi sayısal yaklaşım yöntemleri mevcut kuralları değiştirebilir. Bunlar sessizce optimizasyon olarak eklenemez; ayrı tasarım önerisi, hata ölçümü ve kullanıcı onayı gerektirir.

### 13.4. Bellek ve ölçeklenebilirlik

- Gereksiz tüm-çift ilişkileri, her adım için tekrar oluşturulan ara listeler ve artık kullanılmayan olay/veriler tutulmaz.
- Seyrek ilişki yapıları yalnızca mevcut ilişkileri saklar; yoğun matrisin bellekte gizli biçimde yeniden oluşturulmasına izin verilmez.
- Olay kuyruğunda zamanı geçmiş veya geçersizleşmiş olaylar kontrollü biçimde temizlenir. Temizleme, geçerli olayları veya öğrenme izlerini kaybettirmemelidir.
- Geçici etkinlik izleri ile kalıcı öğrenilmiş bağlantı/parametreler ayrı yaşam döngülerine sahip olmaya devam eder. Bellek temizliği kalıcı öğrenmeyi silemez.
- Veri yapısı seçimi yalnızca teorik işlem karmaşıklığına göre değil, gerçek bellek tüketimi ve uygulama dilinin nesne/erişim maliyetleri ölçülerek yapılır.

### 13.5. Performans doğrulama ve kabul ölçütleri

- Optimizasyon öncesinde ve sonrasında aynı senaryolarla çalışma süresi, olay sayısı, işlenen bileşen sayısı ve bellek tüketimi ölçülür.
- Küçük ağlarda doğruluk ve davranış testleri; daha büyük ağlarda ölçeklenme testleri ayrı yürütülür.
- Seyrek ve yoğun etkileşim, çoklu transmitter salımı, çok dallı feedback, uzun süre sönümlenen potansiyeller ve bağlantı oluşumu/budaması ayrı performans senaryoları olarak ölçülür.
- Her optimizasyon için hem performans testi hem de ilgili davranış/eşdeğerlik testi bulunur.
- Darboğaz ölçülmeden karmaşık optimizasyon eklenmez. Ancak mimari en baştan olay-tabanlı ve seyrek veri kullanımını destekleyecek biçimde kurulur.
- Belirli bir donanımda veya ağ büyüklüğünde sıfır performans sorunu garanti edilemez. Hedef, ölçülebilir ölçek sınırlarını belirlemek, darboğazları erken bulmak ve sistemin doğruluğunu koruyarak bu sınırları iyileştirmektir.

Bu bölümdeki stratejiler hesaplama yöntemini düzenler; nöronların, dendritlerin, sinapsların, kimyasal sinyallerin veya bağlantıların biyolojik esinli yerel davranış kurallarını değiştirmez. Kodlama ve test aşamasında her optimizasyon bu sözleşmeye göre değerlendirilir.

