import random
from collections import deque
from pathlib import Path

from BrainNew.Beyin import Beyin
from BrainNew.ActivationTrace import ActivationTrace


# Ayni ag, veri bolumu, seed, epoch ve zaman adimi ayarlari.
# Bu dosya mevcut deneyi degistirmez; yalnizca gozlem ekleyerek tekrarlar.
GIZLI_NORON_SAYISI = 100
AG_SEED = 42
KARISTIRMA_SEED = 43
ADIM_SAYISI = 20
MAKS_EPOCH = 200
ERKEN_DURDURMA_ESIGI = 5

CIKTI_DOSYASI = Path(__file__).with_name("bilesik_oruntu_takip.txt")

egitim_oruntuleri = [
    ([1, 0, 0], [1]),
    ([1, 0, 1], [1]),
    ([1, 1, 0], [1]),
    ([0, 0, 0], [0]),
    ([0, 0, 1], [0]),
    ([0, 1, 0], [0]),
]

test_oruntuleri = [
    ([1, 1, 1], [1]),
    ([0, 1, 1], [0]),
]


def baglantilari_topla(beyin):
    return {
        baglanti
        for noron in beyin.noronlar
        for akson in noron.aksonlar
        for baglanti in akson.baglantilar
    }


def ag_ozeti(beyin):
    baglantilar = baglantilari_topla(beyin)
    aktif = [b for b in baglantilar if b.aktif]
    etkiler = [b.etki_mv for b in aktif]
    return {
        "noron": len(beyin.noronlar),
        "dendrit": sum(len(n.dendritler) for n in beyin.noronlar),
        "akson_terminali": sum(len(n.aksonlar) for n in beyin.noronlar),
        "baglanti_toplami": len(baglantilar),
        "aktif_baglanti": len(aktif),
        "uyarici": sum(w > 0 for w in etkiler),
        "baskilayici": sum(w < 0 for w in etkiler),
        "sifir_etkili": sum(w == 0 for w in etkiler),
        "etki_toplami": sum(etkiler),
        "mutlak_etki_toplami": sum(abs(w) for w in etkiler),
    }


def ozet_satiri(ozet):
    return (
        f"noron={ozet['noron']}, dendrit={ozet['dendrit']}, "
        f"akson_terminali={ozet['akson_terminali']}, "
        f"aktif_baglanti={ozet['aktif_baglanti']}, "
        f"uyarici={ozet['uyarici']}, baskilayici={ozet['baskilayici']}, "
        f"sifir_etkili={ozet['sifir_etkili']}, "
        f"etki_toplami={ozet['etki_toplami']:.4f}, "
        mutlak_etki_toplami={ozet['mutlak_etki_toplami']:.4f}"
    )


def noron_etiketi(noron, beyin):
    if noron in beyin.reseptor_noronlari:
        return f"R{beyin.reseptor_noronlari.index(noron)}"
    if noron in beyin.ara_noronlar:
        return f"A{beyin.ara_noronlar.index(noron)}"
    if noron in beyin.motor_noronlari:
        return f"M{beyin.motor_noronlari.index(noron)}"
    return "?"


def uygun_baglantilar(noron):
    """Noron.geri_bildirim icindeki yerel iz olusturma adimini salt okunur taklit eder."""
    uygun = []
    for dendrit in noron.dendritler:
        for baglanti in tuple(dendrit.gelen_baglantilar):
            if not baglanti.aktif:
                continue

            iz = baglanti.uygunluk_izi
            katki = noron.birikmis_sinaptik_katkilar.get(baglanti, 0.0)
            if abs(katki) > noron.KATKI_ESIGI:
                iz = min(5.0, iz + 1.0)

            if iz > noron.GERI_BILDIRIM_IZ_ESIGI:
                uygun.append(baglanti)
    return uygun


def geri_bildirim_yolunu_hesapla(baslangic, beyin):
    """Gercek feedback cagrisindan once, mevcut kuralla ulasilacak yolu hesaplar."""
    kuyruk = deque([(baslangic, 0)])
    ziyaret = set()
    katmanlar = {}
    uygun_baglanti_sayisi = 0
    yol_baglantilari = []

    while kuyruk:
        noron, derinlik = kuyruk.popleft()
        if noron in ziyaret:
            continue
        ziyaret.add(noron)
        katmanlar[derinlik] = katmanlar.get(derinlik, 0) + 1

        yerel = uygun_baglantilar(noron)
        uygun_baglanti_sayisi += len(yerel)
        yol_baglantilari.extend(yerel)

        for baglanti in yerel:
            kaynak_noron = baglanti.kaynak.noron
            if kaynak_noron not in ziyaret:
                kuyruk.append((kaynak_noron, derinlik + 1))

    return ziyaret, katmanlar, uygun_baglanti_sayisi, yol_baglantilari


def deneme_ozeti(girdi, beklenen, cikti, trace, beyin):
    ateslenmeler = [
        olay for olay in trace.olaylar if olay["tur"] == "ateslenme"
    ]
    aktarimlar = [
        olay for olay in trace.olaylar if olay["tur"] == "aktarim"
    ]

    reseptor_ateslenmeleri = [
        olay for olay in ateslenmeler
        if olay["noron"] in beyin.reseptor_noronlari
    ]
    ara_ateslenmeleri = [
        olay for olay in ateslenmeler
        if olay["noron"] in beyin.ara_noronlar
    ]
    motor_ateslenmeleri = [
        olay for olay in ateslenmeler
        if olay["noron"] in beyin.motor_noronlari
    ]

    motor = beyin.motor_noronlari[0]
    motor_aktarimlari = [
        olay for olay in aktarimlar if olay["hedef"] is motor
    ]
    pozitif = [o for o in motor_aktarimlari if o["etki_mv"] > 0]
    negatif = [o for o in motor_aktarimlari if o["etki_mv"] < 0]

    return {
        "girdi": girdi,
        "beklenen": beklenen,
        "cikti": cikti,
        "dogru": cikti == beklenen,
        "ateslenen_reseptor": sorted(
            noron_etiketi(o["noron"], beyin) for o in reseptor_ateslenmeleri
        ),
        "ateslenen_ara": sorted(
            noron_etiketi(o["noron"], beyin) for o in ara_ateslenmeleri
        ),
        "ateslenen_motor": sorted(
            noron_etiketi(o["noron"], beyin) for o in motor_ateslenmeleri
        ),
        "motor_aktarim_adedi": len(motor_aktarimlari),
        "motor_pozitif_adet": len(pozitif),
        "motor_negatif_adet": len(negatif),
        "motor_etki_toplami": sum(o["etki_mv"] for o in motor_aktarimlari),
        "motor_pozitif_toplam": sum(o["etki_mv"] for o in pozitif),
        "motor_negatif_toplam": sum(o["etki_mv"] for o in negatif),
        "motor_maks_zaman": max(
            (o["zaman"] for o in motor_aktarimlari), default=None
        ),
    }


def satir_yaz(dosya, metin=""):
    dosya.write(metin + "\n")


def deneme_raporla(dosya, baslik, sonuc, beyin, trace, geri_bildirim=None):
    satir_yaz(dosya, f"  {baslik}")
    satir_yaz(
        dosya,
        f"    girdi={sonuc['girdi']} beklenen={sonuc['beklenen']} "
        f"cikti={sonuc['cikti']} dogru={sonuc['dogru']}"
    )
    satir_yaz(
        dosya,
        f"    ateslenmeler: reseptor={sonuc['ateslenen_reseptor']} "
        f"ara={sonuc['ateslenen_ara']} motor={sonuc['ateslenen_motor']}"
    )
    satir_yaz(
        dosya,
        f"    motora ulasan aktarim: adet={sonuc['motor_aktarim_adedi']} "
        f"uyarici_adet={sonuc['motor_pozitif_adet']} "
        f"baskilayici_adet={sonuc['motor_negatif_adet']} "
        f"toplam_etki={sonuc['motor_etki_toplami']:.4f} "
        f"(+{sonuc['motor_pozitif_toplam']:.4f} / "
        f"{sonuc['motor_negatif_toplam']:.4f}) "
        f"son_aktarim_zamani={sonuc['motor_maks_zaman']}"
    )

    if geri_bildirim is not None:
        ziyaret, katmanlar, uygun_sayi, uygunlar = geri_bildirim
        satir_yaz(
            dosya,
            f"    feedback yolu: ziyaret_edilecek_noron={len(ziyaret)} "
            f"katmanlar={dict(sorted(katmanlar.items()))} "
            f"uygun_baglanti={uygun_sayi}"
        )
        satir_yaz(
            dosya,
            "    feedback uygun baglantilari: "
            + (
                ", ".join(
                    f"{noron_etiketi(b.kaynak.noron, beyin)}->"
                    f"{noron_etiketi(b.hedef.noron, beyin)}"
                    f"(iz={b.uygunluk_izi:.3f}, etki={b.etki_mv:.3f})"
                    for b in uygunlar
                )
                if uygunlar else "YOK"
            )
        )


def main():
    trace = ActivationTrace()
    beyin = Beyin(
        girdi_sayisi=3,
        cikti_sayisi=1,
        ara_noron_sayisi=GIZLI_NORON_SAYISI,
        seed=AG_SEED,
        trace=trace,
    )
    motor = beyin.motor_noronlari[0]
    karistirici = random.Random(KARISTIRMA_SEED)

    with CIKTI_DOSYASI.open("w", encoding="utf-8") as dosya:
        satir_yaz(dosya, "BRAINNEW - BILESİK ORUNTU ADIM ADIM TAKIP")
        satir_yaz(dosya, "=" * 100)
        satir_yaz(
            dosya,
            f"seed={AG_SEED}, gizli_noron={GIZLI_NORON_SAYISI}, "
            f"adim={ADIM_SAYISI}, max_epoch={MAKS_EPOCH}"
        )
        satir_yaz(dosya, "Gorev: [x1,x2,x3] -> [x1]")
        satir_yaz(dosya, "")
        satir_yaz(dosya, "BASLANGIC AGI")
        baslangic_ozeti = ag_ozeti(beyin)
        satir_yaz(dosya, "  " + ozet_satiri(baslangic_ozeti))
        satir_yaz(dosya, "")

        # Egitim oncesi degerlendirme: test verisi yalnizca raporlanir.
        satir_yaz(dosya, "EGITIM ONCESI")
        for girdi, beklenen in egitim_oruntuleri + test_oruntuleri:
            trace.temizle()
            cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
            sonuc = deneme_ozeti(girdi, beklenen, cikti, trace, beyin)
            deneme_raporla(dosya, "degerlendirme", sonuc, beyin, trace)
            beyin.deneme_sonu_sifirla()
        satir_yaz(dosya, "")

        ardisik_tam_basari = 0
        toplam_feedback = 0
        toplam_degisen = 0
        toplam_yeni = 0
        toplam_budanan = 0
        gercek_epoch = 0

        satir_yaz(dosya, "EGITIM")
        for epoch in range(1, MAKS_EPOCH + 1):
            sirali = egitim_oruntuleri.copy()
            karistirici.shuffle(sirali)

            dogru = 0
            feedback_sayisi = 0
            epoch_degisen = 0
            epoch_yeni = 0
            epoch_budanan = 0

            satir_yaz(dosya, "")
            satir_yaz(dosya, f"EPOCH {epoch:03d}")
            satir_yaz(dosya, "-" * 100)

            for sira, (girdi, beklenen) in enumerate(sirali, start=1):
                trace.temizle()
                onceki_baglantilar = baglantilari_topla(beyin)
                onceki_etkiler = {
                    b: b.etki_mv for b in onceki_baglantilar if b.aktif
                }

                cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
                sonuc = deneme_ozeti(girdi, beklenen, cikti, trace, beyin)

                geri_bildirim = None
                degisenler = []
                yeniler = []
                budananlar = []

                if sonuc["dogru"]:
                    dogru += 1
                else:
                    feedback_sayisi += 1
                    deger = 1.0 if beklenen[0] == 1 else -1.0

                    geri_bildirim = geri_bildirim_yolunu_hesapla(
                        motor, beyin
                    )
                    beyin.geri_bildirim(
                        deger, baslangic_noronlari=[motor]
                    )

                    simdiki_baglantilar = baglantilari_topla(beyin)
                    yeniler = [
                        b for b in simdiki_baglantilar
                        if b not in onceki_baglantilar and b.aktif
                    ]
                    budananlar = [
                        b for b in onceki_baglantilar
                        if b.aktif is False
                    ]
                    for b, eski_etki in onceki_etkiler.items():
                        if b.aktif and abs(b.etki_mv - eski_etki) > 1e-12:
                            degisenler.append(
                                (b, eski_etki, b.etki_mv)
                            )

                epoch_degisen += len(degisenler)
                epoch_yeni += len(yeniler)
                epoch_budanan += len(budananlar)
                toplam_degisen += len(degisenler)
                toplam_yeni += len(yeniler)
                toplam_budanan += len(budananlar)

                deneme_raporla(
                    dosya,
                    f"oruntu {sira}/6, feedback={not sonuc['dogru']}",
                    sonuc,
                    beyin,
                    trace,
                    geri_bildirim,
                )
                satir_yaz(
                    dosya,
                    f"    yapisal/plastik sonuc: agirligi_degisen={len(degisenler)} "
                    f"yeni={len(yeniler)} budanan={len(budananlar)}"
                )

                for b, eski, yeni in degisenler:
                    satir_yaz(
                        dosya,
                        f"      agirlik: {noron_etiketi(b.kaynak.noron, beyin)}->"
                        f"{noron_etiketi(b.hedef.noron, beyin)} "
                        f"{eski:.4f}->{yeni:.4f}"
                    )
                for b in yeniler:
                    satir_yaz(
                        dosya,
                        f"      YENI: {noron_etiketi(b.kaynak.noron, beyin)}->"
                        f"{noron_etiketi(b.hedef.noron, beyin)} "
                        f"etki={b.etki_mv:.4f}"
                    )
                for b in budananlar:
                    satir_yaz(
                        dosya,
                        f"      BUDANDI: {noron_etiketi(b.kaynak.noron, beyin)}->"
                        f"{noron_etiketi(b.hedef.noron, beyin)}"
                    )

                beyin.deneme_sonu_sifirla()

            toplam_feedback += feedback_sayisi
            ag = ag_ozeti(beyin)
            satir_yaz(
                dosya,
                f"  EPOCH OZETI: dogru={dogru}/6 feedback={feedback_sayisi} "
                f"agirlik_degisim={epoch_degisen} yeni={epoch_yeni} "
                f"budama={epoch_budanan}"
            )
            satir_yaz(dosya, "  AG: " + ozet_satiri(ag))

            gercek_epoch = epoch
            if dogru == len(egitim_oruntuleri):
                ardisik_tam_basari += 1
            else:
                ardisik_tam_basari = 0

            if ardisik_tam_basari >= ERKEN_DURDURMA_ESIGI:
                satir_yaz(
                    dosya,
                    f"Erken durdurma: {ERKEN_DURDURMA_ESIGI} tam basarili epoch."
                )
                break

        satir_yaz(dosya, "")
        satir_yaz(dosya, "EGITIM SONRASI - FEEDBACKSIZ DEGERLENDIRME")
        for etiket, oruntuler in (
            ("EGITIM", egitim_oruntuleri),
            ("TEST", test_oruntuleri),
        ):
            dogru = 0
            for girdi, beklenen in oruntuler:
                trace.temizle()
                cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
                sonuc = deneme_ozeti(girdi, beklenen, cikti, trace, beyin)
                dogru += int(sonuc["dogru"])
                deneme_raporla(dosya, etiket, sonuc, beyin, trace)
                beyin.deneme_sonu_sifirla()
            satir_yaz(dosya, f"  {etiket} BASARI: {dogru}/{len(oruntuler)}")

        son_ozet = ag_ozeti(beyin)
        satir_yaz(dosya, "")
        satir_yaz(dosya, "GENEL SONUC")
        satir_yaz(dosya, f"  gercek_epoch={gercek_epoch}")
        satir_yaz(dosya, f"  toplam_feedback={toplam_feedback}")
        satir_yaz(dosya, f"  toplam_agirlik_degisen_baglanti={toplam_degisen}")
        satir_yaz(dosya, f"  toplam_yeni_baglanti={toplam_yeni}")
        satir_yaz(dosya, f"  toplam_budanan_baglanti={toplam_budanan}")
        satir_yaz(dosya, "  BASLANGIC: " + ozet_satiri(baslangic_ozeti))
        satir_yaz(dosya, "  BITIS:     " + ozet_satiri(son_ozet))

    print(f"Takip raporu olusturuldu: {CIKTI_DOSYASI}")


if __name__ == "__main__":
    main()
