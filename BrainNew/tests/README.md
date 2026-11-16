# BrainNew — Ayrı test paketleri

Bu testler prototipte uygulanmış davranışları denetler. Bağımsız mikroglia bakımı, yerel budama, kimyasal işaretle kontrollü bağlantı oluşumu, dallanan feedback, seyrek sinaps-sinaps ilişkileri, nöronlar arası zamansal birlikte etkinlik ve nöron-yerel homeostaz için ilk birim/regresyon testleri vardır. Otomatik yapısal büyüme zamanlaması, bağlantı onarımı ve ağ düzeyinde örüntü tamamlama/genelleme henüz kabul kapısından geçmemiştir.

Proje kökünde ve sanal ortam açıkken:

```powershell
python -m pytest BrainNew/tests/test_orchestration.py -v
python -m pytest BrainNew/tests/test_electrical.py -v
python -m pytest BrainNew/tests/test_chemical.py -v
python -m pytest BrainNew/tests/test_microglia.py -v
python -m pytest BrainNew/tests/test_structural_plasticity.py -v
python -m pytest BrainNew/tests/test_experiment_recording.py -v
python -m pytest BrainNew/tests/test_experiment_runner.py -v
```

Hepsini tek seferde çalıştırmak için:

```powershell
python -m pytest BrainNew/tests -v
```

Prototip demosu:

```powershell
python -m BrainNew.main
```

## Paketlerin kapsamı

- `test_orchestration.py`: Simülasyon saati, olay sırası ve önceliği, aynı zaman damgasındaki girdilerin entegrasyondan önce işlenmesi, entegrasyon olaylarının tekilleştirilmesi, tam sinaptik iletim gecikmesi, refrakter dönemde tamponlanan girdinin dinlenmeye dönüşte işlenmesi, olay limiti ve deterministiklik.
- `test_electrical.py`: Membran potansiyeli, eşik, sızıntı, nöronun kendi entegrasyon ve ateşlenme kararı, aksiyon potansiyeli fazları, refrakter durum, dendritik işaretli toplama, sinaps yerel potansiyeli, sönüm, seçici aktivasyon, öğrenme ve sayısal girdi doğrulaması.
- `test_experiment_recording.py`: Pasif olay kaydının simülasyon davranışını değiştirmemesi, olay sırasının ve kayıt verisinin korunması.
- `test_experiment_runner.py`: Baseline deney örneklerinin bağımsız çalışması, eğitim/test ayrımı, tekrarlanabilir ölçüm ve doğru/yanlış pozitif-negatif sayımları.
- `test_spatial_index.py`: 2B hücre tabanlı yerel aday arama, yarıçap doğruluğu, deterministik sıralama, kayıt/silme ve konum güncellemesi.
- `test_chemical.py`: Transmitter kaynakları, çoklu salım, tür ayrımı, 2B uzamsal yayılım, zamansal sönüm, analitik yoğunluk formülü, reseptör duyarlılığı ve geçersiz kimyasal kaynak/sorgu değerleri.
- `test_microglia.py`: Bağımsız mikroglia ajanı, algılama yarıçapı, düşük kullanım ile budama sinyalinin birlikte gerekliliği, stabilizasyon, sonlu zaman aralığında periyodik bakım ve Beyin'in yalnızca olay koordinasyonu yapması.
- `test_structural_plasticity.py`: Yerel büyüme sinyali, hedef dendritin pozitif reseptör uygunluğu, yarıçap sınırı, deterministik hedef seçimi, aynı üçlünün tekilleştirilmesi ve yeni bağlantının zayıf/olgunlaşmamış başlangıcı.
- `test_feedback_wave.py`: Pozitif feedback'te aktif/pasif terminal eşik yönleri, nedensel girdiler üzerinden geriye dallanma ve ziyaret edilmiş nöronlarla döngü engelleme.
- `test_plasticity.py`: Sessiz/aşırı etkin nöronlarda eşik homeostazı, hedef etkinlik civarında kararlılık, episode'lar arası uzun dönem izin korunması, sinaptik öğrenilmiş parametrelerin korunması ve homeostaz ablasyonu.
- `test_training_foundation.py`: Kalıcı episode öğrenmesi, yerel feedback, sinaps/nöron ilişkileri ve eğitim yürütücüsü temel davranışları.

## Testlerin yorumlanması

Bir testin geçmesi, test edilen yazılım davranışının yazılmış beklentiyle uyumlu olduğunu gösterir; biyolojik doğruluğu veya tasarımın tamamlandığını kanıtlamaz. Başarısız testleri düzeltmeden önce hatanın koddan mı, test varsayımından mı, yoksa henüz kararlaştırılmamış tasarım davranışından mı kaynaklandığı ayrılmalıdır.

Refrakter dönemde gelen girdilerin yaşam döngüsü tasarım sözleşmesinde hâlâ açık karardır. Mevcut düzeltme dalı bunları tamponda tutup nöron dinlenmeye döndüğünde yeniden bütünleştiren geçici davranışı test eder; bu test nihai biyolojik/tasarım kararının verildiği anlamına gelmez.

Testlerin geçtiği iddiası yalnızca komutlar gerçekten çalıştırıldıktan sonra verilmelidir.