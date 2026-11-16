# BrainNew — Ayrı test paketleri

Bu testler prototipte uygulanmış davranışları denetler. Henüz uygulanmamış mikroglia, yapısal plastisite, feedback dallanması, sinaps-sinaps öğrenmesi veya yerel nöron-nöron etkileşimi için başarı iddiası taşımaz.

Proje kökünde ve sanal ortam açıkken:

```powershell
python -m pytest BrainNew/tests/test_orchestration.py -v
python -m pytest BrainNew/tests/test_electrical.py -v
python -m pytest BrainNew/tests/test_chemical.py -v
python -m pytest BrainNew/tests/test_experiment_recording.py -v
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
- `test_chemical.py`: Transmitter kaynakları, çoklu salım, tür ayrımı, 2B uzamsal yayılım, zamansal sönüm, analitik yoğunluk formülü, reseptör duyarlılığı ve geçersiz kimyasal kaynak/sorgu değerleri.

## Testlerin yorumlanması

Bir testin geçmesi, test edilen yazılım davranışının yazılmış beklentiyle uyumlu olduğunu gösterir; biyolojik doğruluğu veya tasarımın tamamlandığını kanıtlamaz. Başarısız testleri düzeltmeden önce hatanın koddan mı, test varsayımından mı, yoksa henüz kararlaştırılmamış tasarım davranışından mı kaynaklandığı ayrılmalıdır.

Refrakter dönemde gelen girdilerin yaşam döngüsü tasarım sözleşmesinde hâlâ açık karardır. Mevcut düzeltme dalı bunları tamponda tutup nöron dinlenmeye döndüğünde yeniden bütünleştiren geçici davranışı test eder; bu test nihai biyolojik/tasarım kararının verildiği anlamına gelmez.

Testlerin geçtiği iddiası yalnızca komutlar gerçekten çalıştırıldıktan sonra verilmelidir.