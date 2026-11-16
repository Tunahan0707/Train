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
- [x] Seed'li, 2B uzamsal ve seyrek başlangıç ağı kurucusu eklendi; topoloji ve başlangıç parametreleri seed ile tekrarlanabilir.

## Henüz tamamlanmayan sprint başlıkları

- Seed'li seyrek ağ kurucunun kapsamlı yapılandırma, erişilebilirlik ve istatistik raporları.

- Feedback'in çoklu dal, döngü, gecikme, iz eşiği ve pozitif/negatif yönlerde kapsamlı davranış doğrulaması.
- Bağlantısız nöron toparlanması, otomatik büyüme zamanlaması ve onarım kalibrasyonu.
- Davranışsal örüntü geri çağırma, genelleme ve matematik görevleri.
- Ablasyon, çoklu seed kalibrasyonu ve ölçek ölçümleri.

## Doğrulama durumu

Yeni feedback dallanması için regresyon testleri eklendi. Bu oturumda test paketi henüz çalıştırılmadı; yeşil kabul edilmemelidir. Testler çalıştırılmadan başarılı kabul edilmeyecektir.
