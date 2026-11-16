from collections import defaultdict

from BrainNew.beyin_ogrenme_stratejileri_deneyi import (
    ADIM_SAYISI,
    TUM_ORUNTULER,
    karma_ogretme,
)


INCELENECEKLER = [
    ([0, 1, 0], [0]),
    ([0, 0, 1], [0]),
    ([0, 1, 1], [0]),
]


def noron_etiketi(beyin, noron):
    gruplar = (
        ("R", beyin.reseptor_noronlari),
        ("A", beyin.ara_noronlar),
        ("M", beyin.motor_noronlari),
    )
    for onek, liste in gruplar:
        try:
            return f"{onek}{liste.index(noron):03d}"
        except ValueError:
            pass
    return "?"


def gozlemciyi_bagla(beyin):
    """Model davranisini degistirmeden dendrit tuketimini ve noron durumunu kaydeder."""
    baslangic_zamani = beyin.zaman
    aktarimlar = []
    noron_durumlari = []
    orijinal_metotlar = []

    for noron in beyin.noronlar:
        etiket = noron_etiketi(beyin, noron)
        for dendrit_no, dendrit in enumerate(noron.dendritler):
            orijinal = dendrit.etkileri_al
            orijinal_metotlar.append((dendrit, "etkileri_al", orijinal))

            def gozlenen_etkileri_al(
                _orijinal=orijinal,
                _etiket=etiket,
                _dendrit_no=dendrit_no,
            ):
                toplam, katkilar = _orijinal()
                for baglanti, etki_mv in katkilar:
                    aktarimlar.append({
                        "zaman": beyin.zaman - baslangic_zamani,
                        "kaynak": noron_etiketi(beyin, baglanti.kaynak.noron),
                        "hedef": _etiket,
                        "dendrit": _dendrit_no,
                        "etki_mv": etki_mv,
                        "agirlik_mv": baglanti.etki_mv,
                    })
                return toplam, katkilar

            dendrit.etkileri_al = gozlenen_etkileri_al

    for noron in beyin.noronlar:
        etiket = noron_etiketi(beyin, noron)
        orijinal = noron.guncelle
        orijinal_metotlar.append((noron, "guncelle", orijinal))

        def gozlenen_guncelle(
            _orijinal=orijinal,
            _etiket=etiket,
            _noron=noron,
        ):
            ateslendi = _orijinal()
            if _etiket.startswith("M") or (
                _etiket.startswith("A") and ateslendi
            ):
                noron_durumlari.append({
                    "zaman": beyin.zaman - baslangic_zamani,
                    "noron": _etiket,
                    "membran_mv": _noron.membran_potansiyeli,
                    "durum": _noron.durum,
                    "ateslendi": ateslendi,
                })
            return ateslendi

        noron.guncelle = gozlenen_guncelle

    def geri_al():
        for nesne, ad, orijinal in orijinal_metotlar:
            setattr(nesne, ad, orijinal)

    return aktarimlar, noron_durumlari, geri_al


def denemeyi_incele(beyin, girdi, beklenen):
    beyin.deneme_sonu_sifirla()
    aktarimlar, durumlar, geri_al = gozlemciyi_bagla(beyin)

    try:
        cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
    finally:
        geri_al()

    motor_aktarimlari = [
        olay for olay in aktarimlar if olay["hedef"].startswith("M")
    ]
    ara_ateslenmeleri = [
        olay for olay in durumlar
        if olay["noron"].startswith("A") and olay["ateslendi"]
    ]
    motor_durumlari = [
        olay for olay in durumlar if olay["noron"].startswith("M")
    ]

    print("\n" + "=" * 88)
    print(
        f"GIRDI {girdi} | BEKLENEN {beklenen} | CIKTI {cikti} | "
        f"{'DOGRU' if cikti == beklenen else 'YANLIS'}"
    )
    print("-" * 88)

    print("Ara noron ateslenmeleri:")
    if ara_ateslenmeleri:
        for olay in ara_ateslenmeleri:
            print(
                f"  t={olay['zaman']:02d} ms | {olay['noron']} | "
                f"membran={olay['membran_mv']:.3f} mV"
            )
    else:
        print("  Hicbir ara noron ateslenmedi.")

    print("\nMotora ulasan sinaptik katkilar:")
    if motor_aktarimlari:
        zamana_gore = defaultdict(list)
        for olay in motor_aktarimlari:
            zamana_gore[olay["zaman"]].append(olay)

        for zaman in sorted(zamana_gore):
            olaylar = zamana_gore[zaman]
            toplam = sum(o["etki_mv"] for o in olaylar)
            print(
                f"  t={zaman:02d} ms | toplam yeni katkı={toplam:+.3f} mV"
            )
            for olay in olaylar:
                print(
                    f"    {olay['kaynak']} -> {olay['hedef']} "
                    f"(dendrit {olay['dendrit']}) | "
                    f"anlik={olay['etki_mv']:+.3f} mV | "
                    f"sinaps agirligi={olay['agirlik_mv']:+.3f} mV"
                )
    else:
        print("  Motora sinaptik aktarim ulasmadi.")

    print("\nMotor membran potansiyeli:")
    for olay in motor_durumlari:
        print(
            f"  t={olay['zaman']:02d} ms | "
            f"{olay['membran_mv']:+.3f} mV | "
            f"durum={olay['durum']} | "
            f"ateslendi={'EVET' if olay['ateslendi'] else 'HAYIR'}"
        )

    print("\nOzet:")
    print(f"  Ara noron ateslenme sayisi: {len(ara_ateslenmeleri)}")
    print(f"  Motora gelen aktarim sayisi: {len(motor_aktarimlari)}")
    print(
        "  Motor ateslenme zamanlari: "
        + str([o["zaman"] for o in motor_durumlari if o["ateslendi"]])
    )
    print(f"  Son cikti: {cikti}")

    beyin.deneme_sonu_sifirla()


def main():
    print("=" * 88)
    print("BILESIK ORUNTU NEDENSEL YOL TESHISI")
    print("Tek ag, tek egitim, feedback uygulanmayan gozlem denemeleri")
    print("=" * 88)

    # Onceki karma deneyle ayni seed, egitim oruntuleri ve durdurma kriteri.
    beyin, epoch, feedback, tamamlandi = karma_ogretme(TUM_ORUNTULER)

    print("\nEGITIM OZETI")
    print(f"Epoch: {epoch} | Geri bildirim: {feedback}")
    print(f"Ogretim kriteri: {'TAMAM' if tamamlandi else 'TAMAMLANMADI'}")

    for girdi, beklenen in INCELENECEKLER:
        denemeyi_incele(beyin, girdi, beklenen)


if __name__ == "__main__":
    main()
