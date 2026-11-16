# BrainNew — İlk Prototip Durumu

Dal: `experiment/dendritic-synaptic-potentials`

Bu belge, tasarım sözleşmesinin yerine geçmez. İlk çalışan prototipte hangi parçaların bulunduğunu ve henüz hangi kararların/uygulamaların eksik olduğunu takip eder.

## Prototip 0.1 — Uygulanan çekirdek

- `Beyin.py`: Simülasyon saati ve deterministik, zaman öncelikli olay kuyruğu. Beyin öğrenme kararı vermez; olayları ilgili bileşenlere dağıtır.
- `Noron.py`: Membran potansiyeli, zamana bağlı lazy sızıntı ve depolarizasyon → repolarizasyon → hiperpolarizasyon döngüsü.
- `Dendrid.py`: İşaretli elektriksel girdileri toplar; transmitter reseptör yanıtını yerel sinyale modülatör olarak ekler; dendrit-sinaps katkılarını taşır.
- `Baglanti.py`: Yerel aktivasyon potansiyeli, eşik, lazy sönüm, etkinlik izi başlangıcı ve hedefe pozitif iletim gecikmesi.
- `KimyasalAlan.py`: Her transmitter türü için ayrı kaynakları tutan, 2B analitik difüzyon/sönüm alanı.
- Bir terminalin aynı aktivasyon olayında birden fazla transmitter türü salabilmesi desteklenir.
- Bir nöron ateşlendiğinde yalnızca yerel potansiyeli eşiği karşılayan çıkış sinapsları aktive edilir.
- Bir sinapsa birden fazla dendritten gelen etkiler önce toplamsal hesaplanır, sonra o sinapsa o olayda katkı veren dendrit sayısının kareköküyle normalize edilir.
- Dendrit-sinaps öğrenmesi yalnızca gerçekten sıfırdan farklı katkı yüklenmiş çiftlerde yürür. İlk değerlendirme fırsatında negatif ceza uygulanmaz.
- Olay kuyruğunda aynı zamanlı girdiler, entegrasyon olayından önce toplanır; olay kimliği eşit zamanlarda deterministik sıra sağlar.

## İlk doğrulama

`BrainNew/tests/test_brain.py` içinde sekiz test bulunur:

1. Duyusal girdiden nöron ateşlenmesine ve hedef nörona iletime.
2. Yalnızca yerel eşiği geçen çıkış sinapsının aktive olması.
3. Bir sinapsa katkı veren birden fazla dendrit için sinaps-başına karekök normalizasyonu.
4. Yalnızca gerçekten katkı yükleyen dendrit-sinaps çiftinin öğrenilmesi.
5. Yerel potansiyelin sınırlar içinde kalması ve lazy sönümü.
6. Refrakter durumdayken yeniden aksiyon potansiyeli başlatılamaması.
7. Tek terminalden birden fazla transmitter türünün birlikte salınması.
8. Kimyasal türlerin ayrı tutulması ve alanın uzay/zamanda azalması.

Çalıştırma komutu:

```bash
python -m unittest discover -s BrainNew/tests -v
```

Mevcut dosya içeriklerinin izole bir yerel kopyasında sekiz testin tamamı geçti. GitHub dalının doğrudan checkout'u bu çalışma ortamında yapılamadığı için testler uzak dal üzerinde çalıştırılmış sayılmaz; yerel kopya doğrulamasıdır.

## Henüz uygulanmayan tasarım parçaları

Bunlar unutulmuş veya iptal edilmiş değildir; sonraki prototip aşamalarına bırakılmıştır.

- Yönlü sinaps-sinaps ilişkileri, birlikte etkinleşme ve etkinleşmeme öğrenmesi.
- Geriye doğru dallanan feedback, dal başına iz eşiği ve sıralı feedback olayları.
- Farklı nöronların uzamsal/zamansal yakınlıkla birlikte ateşlenme etkileşimi.
- Bağlantı nesnesine ait mikroglia-benzeri yerel koruma, yaşlanma, yeniden şekillenme ve budama.
- Kopmuş bağlantı yerine yeni bağlantı oluşumu, mevcut zayıf bağlantının onarımı ve bağlantısız nöronun toparlanma modu.
- Reseptör organı ve motor organı üzerinden tam duyusal/çıktısal arayüz. Şimdilik duyusal girdi doğrudan dendrite olay olarak verilir.
- Geçici izlerin dallar boyunca nedensel takibi ve episode yaşam döngüsü.
- Bağlantı repertuvarı/topolojisi için dendritlerle akson terminallerinin eşleştirilme kuralı.
- Büyük ağlarda kimyasal kaynak sorgusunun hızlandırılması ve kaynak belleğinin yaşam döngüsü.

## Bilinçli olarak açık bırakılan davranış

Refrakter dönemde gelen girdilerin tutulması, sönümlenmesi veya kaybolması henüz tasarımda kararlaştırılmadı. İlk kodda dendrit giriş tamponunda kalırlar; refrakter dönemdeki entegrasyon olayı ateşlenme üretmez. Dinlenmeye dönüşten sonra otomatik entegrasyon henüz planlanmadığından, bekleyen girdiler sonraki bir entegrasyon olayı gelene kadar bekleyebilir. Bu geçici uygulama nihai davranış kararı değildir.

Kimyasal alanın kaynakları şimdilik silinmez; yoğunluk sorgusu bütün kayıtlı kaynakları dolaşır. Bu, küçük prototip için kabul edilen geçici sınırlamadır; büyük ağ performansı olarak sunulamaz.

Kimyasal reseptör yanıtının dendritik yerel sinyale eklenişi, difüzyon parametreleri ve diğer sayısal değerler kalibrasyon gerektiren başlangıç tercihleridir; biyolojik sabit değildir.

## Sonraki sıra

1. Refrakter dönemde gelen girdilerin yaşam döngüsünü kesinleştir ve test et.
2. Aktivite izi ve yönlü sinaps-sinaps ilişkilerini ekle.
3. Feedback dallanmasını, gecikmelerini ve deterministik sıralamasını ekle.
4. Kimyasal sinyal sınıflarını bağlantı-yerel mikroglia-benzeri kurallara bağla.
5. Yapısal plastisite, yeni bağlantı oluşumu ve toparlanma modunu ekle.
6. Yerel nöron-nöron etkileşimini, ardından reseptör/motor organlarını tamamla.
7. Her aşamada davranış testleri ve performans ölçümleri ekle.
