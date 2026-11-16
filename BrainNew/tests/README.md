# BrainNew — Test paketi

Bu paket, mevcut prototipteki yazılım davranışlarını ve kontrollü deney düzeneklerini sınar. Test başarısı biyolojik doğruluk veya genel öğrenme kapasitesi kanıtı değildir.

Proje kökünde, sanal ortam açıkken:

```powershell
python -m pytest BrainNew/tests -v
python -m BrainNew.main
```

## Çekirdek ve mimari

- test_signal_propagation.py: duyusal girdiden kaynak nöron ateşlenmesine ve sinaptik iletim üzerinden hedef nörona uçtan uca yayılım.
- test_orchestration.py: olay kuyruğu, zamanlama, olay önceliği, entegrasyon tekilleştirme, gecikmeli iletim, refrakter girdi ve deterministiklik.
- test_electrical.py: membran, aksiyon potansiyeli, dendrit entegrasyonu, seçici terminal aktivasyonu, Hebbian/STDP, uygunluk izi ve elektriksel davranışlar.
- test_chemical.py: kimyasal kaynaklar, uzamsal/zamansal yayılım, transmitter ayrımı, reseptör yanıtı, gecikmiş modülasyon ve kaynak temizliği.
- test_microglia.py: bağımsız mikroglia ajanları, yerel bakım, stabilizasyon, budama ve fiziksel kopma koşulları.
- test_structural_plasticity.py: yerel aday arama, hedef uygunluğu, bağlantı tekilleştirme, zayıf başlangıç ve kayıt tutarlılığı.
- test_spatial_index.py: 2B uzamsal indeksin arama yarıçapı, sıralama, kayıt, silme ve konum güncellemesi.
- test_network_builder.py: seed'li seyrek başlangıç ağının tekrarlanabilirliği ve yapılandırma doğrulaması.
- test_training_foundation.py: episode kalıcılığı, yerel feedback, nedensel geri yayılım, yerel ilişkiler ve eğitim sürücüsü.
- test_feedback_wave.py: dallanan geriye feedback'in yerel ve döngü güvenli davranışı.
- test_neuron_episode_diagnostics.py: pasif nöron/episode tanılama sayaçları.
- test_experiment_recording.py: pasif olay kaydının simülasyon davranışını değiştirmemesi ve kayıt sırası.
- test_experiment_runner.py: baseline deney sürücüsü, eğitim/test ayrımı, bağımsız ağlar ve ölçüm raporu.
- test_activation_trace.py: pasif ateşlenme/sinaps kaydı ve gözlenen olaylardan nedensel yol çıkarımı.

## Öğrenme ve görev deneyleri

- test_memory_recall.py: tek örüntülü kısmi ipucu geri çağırma prototipi.
- test_overlapping_memory.py: ortak elemanlı iki örüntünün seçici geri çağırılması.
- test_contextual_memory.py: aynı ipucunun farklı bağlamlarda farklı örüntüleri çağırması, gürültü ve kanal kaybı taramaları.
- test_numeric_representation.py: popülasyon kodlaması ve sayısal temsil arayüzü.
- test_magnitude_comparison.py: M1 büyüklük karşılaştırma deney düzeneği ve tanılamaları.
- test_binary_magnitude_comparison.py: M2 binary giriş, ara nöron katmanı, eğitim/test ayrımı ve tanılamalar.
- test_plasticity.py: homeostatik eşik güncellemesi ve ablasyon.

## Testlerin kapsam sınırı

- ActivationTrace yalnızca gözlem yapar; Baglanti.uygunluk_izi gibi öğrenme değişkenlerinin yerine geçmez.
- Beyin snapshot kaydetme/yükleme henüz uygulanmadı; ayrı tasarım planı DEVELOPMENT_AND_PERSISTENCE_PLAN.md içindedir.
- Gelişimden boş ağ oluşturma henüz uygulanmadı. Mevcut AgKurucu rastgele seyrek başlangıç ağı, ilerideki gelişim modunun baseline kontrolüdür.
- Eski BrainOld klasörü tarihsel referans olarak korunur; aktif BrainNew test paketi değildir.
- Boş ve yinelenen eski test dosyaları kaldırıldı. Eski geniş test_brain.py kapsamı odaklı elektriksel/kimyasal/orkestrasyon testlerinde zaten kapsandığından kaldırıldı.

Testlerin geçtiği yalnızca komut gerçekten çalıştırıldıktan sonra söylenmelidir.
