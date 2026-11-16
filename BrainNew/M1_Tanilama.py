"""M1 büyüklük karşılaştırması için davranış ve ağırlık tanılaması.

Çekirdek deneyin öğrenme kurallarını değiştirmez. Eğitim boyunca karar
dağılımını, sınıf bazlı doğruluğu ve duyusal projeksiyon ağırlıklarını ölçer.
"""
from BrainNew.M1_BuyuklukKarsilastirma import BuyuklukKarsilastirmaDeneyi


def _agirliklar(deney):
    return {
        sinaps.kimlik: sinaps.sinaptik_agirlik
        for sinaps in deney.sinapslar
    }


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


def _davranis_ozeti(sonuclar, deney):
    """Karar tercihlerini ve iki hedef sınıfındaki başarıyı ayırır."""
    karar_sayilari = {deney.SOL: 0, deney.SAG: 0, None: 0}
    siniflar = {
        deney.SOL: {"ornek": 0, "dogru": 0},
        deney.SAG: {"ornek": 0, "dogru": 0},
    }
    for sonuc in sonuclar:
        karar_sayilari[sonuc["gerceklesen"]] += 1
        beklenen = sonuc["beklenen"]
        siniflar[beklenen]["ornek"] += 1
        siniflar[beklenen]["dogru"] += int(sonuc["dogru"])
    return {
        "karar_dagilimi": karar_sayilari,
        "sinif_bazli": {
            sinif: {
                **deger,
                "dogruluk": (
                    deger["dogru"] / deger["ornek"]
                    if deger["ornek"] else None
                ),
            }
            for sinif, deger in siniflar.items()
        },
    }


def _agirlik_gruplari(deney, baslangic):
    """Duyusal projeksiyonları WTA bağlantılarından ayrı raporlar."""
    gruplar = {
        deney.SOL: {"baslangic": [], "son": [], "delta": []},
        deney.SAG: {"baslangic": [], "son": [], "delta": []},
    }
    wta = []
    for sinaps in deney.sinapslar:
        ilk = baslangic[sinaps.kimlik]
        son = sinaps.sinaptik_agirlik
        if sinaps.kimlik.endswith(":WTA"):
            wta.append((ilk, son))
            continue
        hedef = sinaps.hedef.kimlik
        grup = gruplar[hedef]
        grup["baslangic"].append(ilk)
        grup["son"].append(son)
        grup["delta"].append(son - ilk)

    def istatistik(degerler):
        if not degerler:
            return {"n": 0}
        return {
            "n": len(degerler),
            "ortalama": sum(degerler) / len(degerler),
            "minimum": min(degerler),
            "maksimum": max(degerler),
            "pozitif": sum(x > 1e-12 for x in degerler),
            "negatif": sum(x < -1e-12 for x in degerler),
            "sifir": sum(abs(x) <= 1e-12 for x in degerler),
        }

    sonuc = {}
    for hedef, grup in gruplar.items():
        sonuc[hedef] = {
            "baslangic": istatistik(grup["baslangic"]),
            "son": istatistik(grup["son"]),
            "delta": istatistik(grup["delta"]),
            "ortalama_mutlak_delta": (
                sum(abs(x) for x in grup["delta"]) / len(grup["delta"])
                if grup["delta"] else 0.0
            ),
        }
    sonuc["WTA"] = {
        "baglanti_sayisi": len(wta),
        "ortalama_baslangic": (
            sum(x[0] for x in wta) / len(wta) if wta else None
        ),
        "ortalama_son": (
            sum(x[1] for x in wta) / len(wta) if wta else None
        ),
        "maksimum_mutlak_delta": max(
            (abs(son - ilk) for ilk, son in wta), default=0.0
        ),
    }
    return sonuc



def _sinaps_dendrit_katkisi(sinaps):
    """Kaynak nöronun bu terminale bağlı dendritik katkısını bulur."""
    for dendrit in sinaps.kaynak.dendritler.values():
        if sinaps in dendrit.sinaps_katkilari:
            return dendrit.sinaps_katkilari[sinaps]
    return 0.0


def _projeksiyon_imzasi(deney):
    """İşaretli gerçek iletim katsayısını, dendrit kapısını ve olgunluğu ayırır."""
    sonuc = {}
    for sinaps in deney.sinapslar:
        if sinaps.kimlik.endswith(":WTA"):
            continue
        sonuc[sinaps.kimlik] = {
            "kaynak_kanal": "SOL_GIRDI" if sinaps.kaynak.kimlik.startswith("SL") else "SAG_GIRDI",
            "hedef": sinaps.hedef.kimlik,
            "baz_etki": sinaps.etki,
            "sinaptik_agirlik": sinaps.sinaptik_agirlik,
            "yapisal_olgunluk": sinaps.yapisal_olgunluk,
            "iletim_katsayisi": sinaps.iletim_etkisi(),
            "dendrit_katkisi": _sinaps_dendrit_katkisi(sinaps),
            "terminal_aktivasyon_sayisi": sinaps.aktivasyon_sayisi,
        }
    return sonuc


def _projeksiyon_ozeti(imza):
    gruplar = {}
    for kayit in imza.values():
        anahtar = (kayit["kaynak_kanal"], kayit["hedef"])
        gruplar.setdefault(anahtar, []).append(kayit)
    sonuc = {}
    for (kanal, hedef), kayitlar in gruplar.items():
        katsayilar = [x["iletim_katsayisi"] for x in kayitlar]
        katkilar = [x["dendrit_katkisi"] for x in kayitlar]
        sonuc[f"{kanal}->{hedef}"] = {
            "n": len(kayitlar),
            "uyarici_projeksiyon": sum(x > 0 for x in katsayilar),
            "baskilayici_projeksiyon": sum(x < 0 for x in katsayilar),
            "sifir_projeksiyon": sum(x == 0 for x in katsayilar),
            "ortalama_isaretli_iletim": sum(katsayilar) / len(katsayilar),
            "ortalama_mutlak_iletim": sum(abs(x) for x in katsayilar) / len(katsayilar),
            "ortalama_dendrit_katkisi": sum(katkilar) / len(katkilar),
        }
    return sonuc


def _episode_akisini_ozetle(deney, onceki_terminal_aktivasyonlari, episode_iletim_katsayilari):
    """Gerçekleşen terminal aktivasyonlarını kanal/hedef bazında yaklaşık akışa çevirir."""
    gruplar = {}
    for sinaps in deney.sinapslar:
        if sinaps.kimlik.endswith(":WTA"):
            continue
        adet = sinaps.aktivasyon_sayisi - onceki_terminal_aktivasyonlari[sinaps.kimlik]
        if adet <= 0:
            continue
        kanal = "SOL_GIRDI" if sinaps.kaynak.kimlik.startswith("SL") else "SAG_GIRDI"
        anahtar = (kanal, sinaps.hedef.kimlik)
        kayit = gruplar.setdefault(anahtar, {
            "terminal_aktivasyonu": 0,
            "imzali_iletim_toplami": 0.0,
            "uyarici_olay": 0,
            "baskilayici_olay": 0,
        })
        katsayi = episode_iletim_katsayilari[sinaps.kimlik]
        kayit["terminal_aktivasyonu"] += adet
        kayit["imzali_iletim_toplami"] += adet * katsayi
        if katsayi > 0:
            kayit["uyarici_olay"] += adet
        elif katsayi < 0:
            kayit["baskilayici_olay"] += adet
    return {f"{kanal}->{hedef}": kayit for (kanal, hedef), kayit in gruplar.items()}


def _duyusal_ateslenme_sayilari(deney):
    return {
        kimlik: deney.beyin.noronlar[kimlik].ateslenme_sayisi
        for kimlik in deney.sol_noronlari + deney.sag_noronlari
    }


def _kanal_ateslenme_farki(deney, onceki):
    sol = sum(deney.beyin.noronlar[k].ateslenme_sayisi - onceki[k] for k in deney.sol_noronlari)
    sag = sum(deney.beyin.noronlar[k].ateslenme_sayisi - onceki[k] for k in deney.sag_noronlari)
    return {"SOL_GIRDI": sol, "SAG_GIRDI": sag}


def tanilama_calistir(seed=20261120, parca_boyutu=10):
    if parca_boyutu < 1:
        raise ValueError("Parça boyutu en az 1 olmalı.")

    deney = BuyuklukKarsilastirmaDeneyi(seed=seed)
    baslangic = _agirliklar(deney)
    baslangic_projeksiyon = _projeksiyon_imzasi(deney)
    tum_sonuclar = []
    toplam_akim = {}

    print(f"Seed: {seed}")
    print(f"Eğitim örneği: {len(deney.egitim_ornekleri)}")
    print(f"Test örneği: {len(deney.test_ornekleri)}")
    print("Başlangıç sinaptik ağırlıkları kaydedildi.")

    for bas in range(0, len(deney.egitim_ornekleri), parca_boyutu):
        ornekler = deney.egitim_ornekleri[bas:bas + parca_boyutu]
        onceki = _agirliklar(deney)
        sonuclar = []
        for sol, sag in ornekler:
            terminal_onceki = {s.kimlik: s.aktivasyon_sayisi for s in deney.sinapslar}
            episode_katsayilari = {s.kimlik: s.iletim_etkisi() for s in deney.sinapslar}
            duyusal_onceki = _duyusal_ateslenme_sayilari(deney)
            sonuclar.append(deney.episode_calistir(sol, sag, feedback=True))
            akim = _episode_akisini_ozetle(deney, terminal_onceki, episode_katsayilari)
            for anahtar, kayit in akim.items():
                toplam = toplam_akim.setdefault(anahtar, {
                    "terminal_aktivasyonu": 0, "imzali_iletim_toplami": 0.0,
                    "uyarici_olay": 0, "baskilayici_olay": 0,
                })
                for alan, deger in kayit.items():
                    toplam[alan] += deger
            sonuclar[-1]["duyusal_ateslenme"] = _kanal_ateslenme_farki(deney, duyusal_onceki)
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
    egitim_agirlik_gruplari = _agirlik_gruplari(deney, baslangic)
    son_projeksiyon = _projeksiyon_imzasi(deney)
    test_onceki = _agirliklar(deney)
    test_sonuclari = deney.test_et()
    test_sonrasi = _agirliklar(deney)
    test_degisim = max(
        (abs(test_sonrasi[k] - test_onceki[k]) for k in test_onceki),
        default=0.0,
    )

    print("\nEğitim toplamı:", deney.ozetle(tum_sonuclar))
    print("Eğitim davranış tanısı:", _davranis_ozeti(tum_sonuclar, deney))
    print("Eğitim ağırlık tanısı:", egitim_degisim)
    print("Başlangıç işaretli projeksiyonlar:", _projeksiyon_ozeti(baslangic_projeksiyon))
    print("Eğitim sonrası işaretli projeksiyonlar:", _projeksiyon_ozeti(son_projeksiyon))
    print("Eğitim boyunca duyusal terminal akışı:", toplam_akim)
    print("Duyusal ağırlık grupları (başlangıç/son/delta):")
    for hedef, ozet in egitim_agirlik_gruplari.items():
        print(f"  {hedef}: {ozet}")
    print("Test:", deney.ozetle(test_sonuclari))
    print("Test davranış tanısı:", _davranis_ozeti(test_sonuclari, deney))
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
        "egitim_davranis": _davranis_ozeti(tum_sonuclar, deney),
        "test_davranis": _davranis_ozeti(test_sonuclari, deney),
        "egitim_agirlik_gruplari": egitim_agirlik_gruplari,
        "baslangic_projeksiyon_ozeti": _projeksiyon_ozeti(baslangic_projeksiyon),
        "son_projeksiyon_ozeti": _projeksiyon_ozeti(son_projeksiyon),
        "egitim_terminal_akisi": toplam_akim,
        "test_max_agirlik_degisim": test_degisim,
    }


if __name__ == "__main__":
    tanilama_calistir()
