# BrainNew — Ayrı test paketleri

Bu testler mevcut 0.1 prototipinin uygulanmış davranışlarını denetler. Henüz uygulanmamış mikroglia, yapısal plastisite, feedback dallanması veya sinaps-sinaps öğrenmesi için başarı iddiası taşımaz.

Proje ana klasöründe ve sanal ortam açıkken:

```powershell
python -m pytest BrainNew/tests/test_orchestration.py -v
python -m pytest BrainNew/tests/test_electrical.py -v
python -m pytest BrainNew/tests/test_chemical.py -v
```

Hepsini tek seferde çalıştırmak için:

```powershell
python -m pytest BrainNew/tests -v
```

## Paketlerin kapsamı

- `test_orchestration.py`: Simülasyon saati, olay kuyruğu, zaman sırası, eşzamanlı girdiler, iletim gecikmesi, olay limiti ve Beyin'in koordinasyon davranışı.
- `test_electrical.py`: Membran potansiyeli, eşik, sızıntı, aksiyon potansiyeli fazları, refrakter durum, dendritik işaretli toplama, sinaps yerel potansiyeli, sönüm, seçici aktivasyon ve mevcut dendrit-sinaps öğrenmesi.
- `test_chemical.py`: Transmitter kaynakları, çoklu salım, tür ayrımı, 2B uzamsal yayılım, zamansal sönüm, analitik yoğunluk formülü, reseptör duyarlılığı ve elektrik-kimya etkileşimi.

Bir testin geçmesi, test edilen mevcut yazılım davranışının beklentiyle uyumlu olduğunu gösterir; biyolojik doğruluğu veya tasarımın tamamlandığını kanıtlamaz. Başarısız testleri düzeltmeden önce çıktıyı inceleyip hatanın koddan mı, test varsayımından mı, yoksa henüz kararlaştırılmamış tasarım davranışından mı kaynaklandığını ayır.
