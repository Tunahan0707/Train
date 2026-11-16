"""M1 büyüklük karşılaştırması için öğrenme tanılama çalıştırıcısı.

Çekirdek deneyin öğrenme kurallarını değiştirmez; eğitim akışını parçalara
ayırıp doğruluk ve gerçek sinaptik ağırlık değişimlerini raporlar.
"""

from BrainNew.M1_BuyuklukKarsilastirma import BuyuklukKarsilastirmaDeneyi


def _agirliklar(deney):
    return {sinaps.kimlik: sinaps.sinaptik_agirlik for sinaps in deney.sinapslar}


def _degisim_ozeti(deney, onceki):
    degisimler = {
        sinaps.kimlik: sinaps.sinaptik_agirlik - onceki[sinaps.kimlik]
        for sinaps in deney.sinapslar
    }
    mutlak = [abs(deger) for deger in degisimler.values()]
    return {
        "degisen_sinaps": sum(deger > 1e-12 for deger in mutlak),
        "toplam_sinaps": len(mutlak),
        "ortalama_mutlak_degisim": sum(mutlak) / len(mutlak) if mutlak else 0.0,
        "en_buyuk_mutlak_degisim": max(mutlak, default=0.0),
        "modulator_guncellemesi": sum(
            sinaps.modulator_guncelleme_sayisi for sinaps in deney.sinapslar
        ),
        "toplam_modulator_agirlik_degisim": sum(
            sinaps.toplam_modulator_agirlik_degisim
            for sinaps in deney.sinapslar
        ),
        "uygunluk_izi_mutlak_toplam": sum(
            abs(sinaps.uygunluk_izi) for sinaps in deney.sinapslar
        ),
    }


def tanilama_calistir(seed=20261120, parca_boyutu=10):
    if parca_boyutu < 1:
        raise ValueError("Parça boyutu en az 1 olmalı.")

    deney = BuyuklukKarsilastirmaDeneyi(seed=seed)
    baslangic = _agirliklar(deney)
    tum_sonuclar = []

    print(f"Seed: {seed}")
    print(f"Eğitim örneği: {len(deney.egitim_ornekleri)}")
    print(f"Test örneği: {len(deney.test_ornekleri)}")
    print("Başlangıç sinaptik ağırlıkları kaydedildi.")

    for bas in range(0, len(deney.egitim_ornekleri), parca_boyutu):
        ornekler = deney.egitim_ornekleri[bas:bas + parca_boyutu]
        onceki = _agirliklar(deney)
        sonuclar = [
            deney.episode_calistir(sol, sag, feedback=True)
            for sol, sag in ornekler
        ]
        tum_sonuclar.extend(sonuclar)
        degisim = _degisim_ozeti(deney, onceki)
        ozet = deney.ozetle(sonuclar)
        print(
            f"Eğitim {bas + 1}-{bas + len(ornekler)}: "
            f"doğruluk={ozet['dogruluk']:.3f}, "
            f"doğru={ozet['dogru']}/{ozet['ornek_sayisi']}, "
            f"değişen_sinaps={degisim['degisen_sinaps']}/"
            f"{degisim['toplam_sinaps']}, "
            f"ort_mutlak_delta={degisim['ortalama_mutlak_degisim']:.8g}, "
            f"max_delta={degisim['en_buyuk_mutlak_degisim']:.8g}"
        )

    egitim_degisim = _degisim_ozeti(deney, baslangic)
    test_onceki = _agirliklar(deney)
    test_sonuclari = deney.test_et()
    test_sonrasi = _agirliklar(deney)
    test_degisim = max(
        (abs(test_sonrasi[k] - test_onceki[k]) for k in test_onceki),
        default=0.0,
    )

    print("\nEğitim toplamı:", deney.ozetle(tum_sonuclar))
    print("Eğitim ağırlık tanısı:", egitim_degisim)
    print("Test:", deney.ozetle(test_sonuclari))
    print(f"Test sırasında en büyük ağırlık değişimi: {test_degisim:.8g}")

    en_cok_degisenler = sorted(
        (
            (sinaps.kimlik, sinaps.sinaptik_agirlik - baslangic[sinaps.kimlik])
            for sinaps in deney.sinapslar
        ),
        key=lambda oge: abs(oge[1]),
        reverse=True,
    )[:8]
    print("En çok değişen 8 sinaps (kimlik, delta):")
    for kimlik, delta in en_cok_degisenler:
        print(f"  {kimlik}: {delta:+.8g}")

    return {
        "egitim": tuple(tum_sonuclar),
        "test": test_sonuclari,
        "egitim_degisim": egitim_degisim,
        "test_max_agirlik_degisim": test_degisim,
    }


if __name__ == "__main__":
    tanilama_calistir()
