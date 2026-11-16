# BrainNew — Uygulama ilerlemesi

Hedef dal: `fix/brainnew-architecture-audit`

## Uygulananlar

- [x] Aynı simülasyon ağı üzerinde episode'lar arası kalıcı parametreleri koruyan `EgitimSurucusu` temeli eklendi.
- [x] `Beyin.episode_baslat()` geçici nöral durumları temizler; öğrenilmiş sinaptik ağırlıkları, dendrit-terminal katkılarını ve bağlantı topolojisini korur.
- [x] `ReseptorOrgan` ve `MotorOrgan` için en küçük kullanılabilir girdi/çıktı arayüzleri eklendi.
- [x] Nöronun yerel feedback metodu, pozitif feedback'te etkin sinaps eşiğini düşürüp etkin olmayanı yükseltir; negatif feedback bunu tersine çevirir.
- [x] Kopmuş bağlantıdan daha önce kuyruğa alınmış sinaptik olayın hedefe ulaşması engellendi.
- [x] Refrakter dönemde gelen girdi tam genliğiyle bekletilip daha sonra yeniden oynatılmıyor.
- [x] 2B kimyasal difüzyon çekirdeğinin salım anı tekilliği pozitif başlangıç yaşıyla düzenlendi.
- [x] Yeni davranışlar için regresyon testleri eklendi.

## Henüz tamamlanmayan sprint başlıkları

- Seed'li seyrek ağ kurucu ve tam ağ yapılandırma sistemi.
- Feedback'in dallanması, geriye yayılması, gecikmesi ve yerel iz ile sönmesi.
- Sinaps-sinaps yönlü etkileşimlerin birlikte etkinleşmeden öğrenilmesi.
- Nöron-nöron yerel birlikte etkinlik etkileşimi.
- Signed synaptic efficacy: kalıcı sinaptik katsayının işaret değiştirebilmesi.
- Kimyasal kaynakların güvenli yaşam döngüsü/temizliği ve olay tabanlı modülatör integrasyonu.
- Bağlantı olgunlaşması, onarımı ve bağlantısız nöron toparlanma döngüsünün tamamlanması.
- Davranışsal örüntü geri çağırma, genelleme ve matematik görevleri.
- Ablasyon, çoklu seed kalibrasyonu ve ölçek ölçümleri.

## Doğrulama durumu

Bu değişiklikler için testler yazıldı; bu oturumda Python çalışma ortamı üzerinden depo klonlanıp test paketi çalıştırılamadı. GitHub Actions sonucu ayrıca doğrulanmalıdır. Testler çalıştırılmadan başarılı kabul edilmeyecektir.
