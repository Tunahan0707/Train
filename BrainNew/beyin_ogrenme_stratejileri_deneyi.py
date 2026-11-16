import random

from BrainNew.Beyin import Beyin


# Gorev: f(x1, x2, x3) = x1
# Egitim ve test oruntuleri birbirinden kesin olarak ayridir.
#
# Iki strateji karsilastirilir:
# 1. Artimli/tek tek ogretme: Her asamada bir oruntu eklenir.
#    Onceki oruntuler de tekrar sunulur; boylece unutma izlenebilir.
# 2. Karma ogretme: Egitim oruntulerinin tamami bastan itibaren sunulur.
#
# Her iki stratejide de minimum epoch, tam basari ve ardışık basari
# kosullari uygulanir. Test oruntuleri egitim veya erken durdurmada
# kesinlikle kullanilmaz.

GIZLI_NORON_SAYISI = 100
AG_SEED = 42
KARISTIRMA_SEED = 43
ADIM_SAYISI = 32

MIN_EPOCH = 20
MAKS_EPOCH = 200
ERKEN_DURDURMA_ESIGI = 5

# Siniflari dengeli ve artimli ogretmeye uygun bir siralama.
TUM_ORUNTULER = [
    ([1, 0, 0], [1]),
    ([0, 0, 0], [0]),
    ([1, 0, 1], [1]),
    ([0, 0, 1], [0]),
    ([1, 1, 0], [1]),
    ([0, 1, 0], [0]),
]

# 5 oruntu deneyinde son oruntu de testte kalir.
TESTTE_TUTULACAK_BIRLESIK = ([0, 1, 1], [0])
EK_TEST_POZITIF = ([1, 1, 1], [1])


def denemeyi_calistir(beyin, girdi):
    cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)
    beyin.deneme_sonu_sifirla()
    return cikti


def geri_bildirim_uygula(beyin, motor, cikti, beklenen):
    if cikti == beklenen:
        return False

    deger = 1.0 if beklenen[0] == 1 else -1.0
    beyin.geri_bildirim(deger, baslangic_noronlari=[motor])
    return True


def degerlendir(beyin, oruntuler):
    dogru = 0
    sonuclar = []

    for girdi, beklenen in oruntuler:
        cikti = denemeyi_calistir(beyin, girdi)
        basarili = cikti == beklenen
        dogru += int(basarili)
        sonuclar.append((girdi, beklenen, cikti, basarili))

    return dogru, sonuclar


def ag_olustur():
    beyin = Beyin(
        girdi_sayisi=3,
        cikti_sayisi=1,
        ara_noron_sayisi=GIZLI_NORON_SAYISI,
        seed=AG_SEED,
    )
    return beyin, beyin.motor_noronlari[0]


def epoch_calistir(beyin, motor, oruntuler, karistirici):
    sirali_oruntuler = list(oruntuler)
    karistirici.shuffle(sirali_oruntuler)

    dogru = 0
    geribildirim = 0

    for girdi, beklenen in sirali_oruntuler:
        cikti = beyin.isle(girdi, adim_sayisi=ADIM_SAYISI)

        if cikti == beklenen:
            dogru += 1
        elif geri_bildirim_uygula(beyin, motor, cikti, beklenen):
            geribildirim += 1

        beyin.deneme_sonu_sifirla()

    return dogru, geribildirim


def artimli_ogretme(egitim_oruntuleri):
    beyin, motor = ag_olustur()
    karistirici = random.Random(KARISTIRMA_SEED)

    gorulenler = []
    toplam_epoch = 0
    toplam_geribildirim = 0
    tamamlandi = True

    print("\nARTIMLI / TEK TEK OGRETME")
    print("-" * 88)

    for asama, oruntu in enumerate(egitim_oruntuleri, start=1):
        gorulenler.append(oruntu)
        ardisik_tam_basari = 0
        asama_tamamlandi = False

        print(
            f"Asama {asama}: yeni oruntu {oruntu[0]} -> {oruntu[1]} "
            f"| eldeki oruntu sayisi: {len(gorulenler)}"
        )

        for epoch in range(1, MAKS_EPOCH + 1):
            dogru, geribildirim = epoch_calistir(
                beyin, motor, gorulenler, karistirici
            )
            toplam_epoch += 1
            toplam_geribildirim += geribildirim

            if dogru == len(gorulenler):
                ardisik_tam_basari += 1
            else:
                ardisik_tam_basari = 0

            print(
                f"  Asama epoch {epoch:03d} | "
                f"Basari: {dogru}/{len(gorulenler)} | "
                f"Geri bildirim: {geribildirim}"
            )

            if (
                epoch >= MIN_EPOCH
                and ardisik_tam_basari >= ERKEN_DURDURMA_ESIGI
            ):
                asama_tamamlandi = True
                print(
                    f"  Asama tamamlandi: minimum {MIN_EPOCH} epoch "
                    f"ve {ERKEN_DURDURMA_ESIGI} ardışık tam basari saglandi."
                )
                break

        if not asama_tamamlandi:
            tamamlandi = False
            print(
                "  ASAMA BASARISIZ: sonraki oruntuye gecilmiyor; "
                "epoch sinirina ulasildi."
            )
            break

    return beyin, toplam_epoch, toplam_geribildirim, tamamlandi


def karma_ogretme(egitim_oruntuleri):
    beyin, motor = ag_olustur()
    karistirici = random.Random(KARISTIRMA_SEED)

    ardisik_tam_basari = 0
    toplam_geribildirim = 0
    gercek_epoch = 0
    tamamlandi = False

    print("\nKARMA / BUTUN ORUNTULERI BIRLIKTE OGRETME")
    print("-" * 88)

    for epoch in range(1, MAKS_EPOCH + 1):
        dogru, geribildirim = epoch_calistir(
            beyin, motor, egitim_oruntuleri, karistirici
        )
        gercek_epoch = epoch
        toplam_geribildirim += geribildirim

        if dogru == len(egitim_oruntuleri):
            ardisik_tam_basari += 1
        else:
            ardisik_tam_basari = 0

        print(
            f"Epoch {epoch:03d} | "
            f"Basari: {dogru}/{len(egitim_oruntuleri)} | "
            f"Geri bildirim: {geribildirim}"
        )

        if (
            epoch >= MIN_EPOCH
            and ardisik_tam_basari >= ERKEN_DURDURMA_ESIGI
        ):
            tamamlandi = True
            print(
                f"Egitim tamamlandi: minimum {MIN_EPOCH} epoch "
                f"ve {ERKEN_DURDURMA_ESIGI} ardışık tam basari saglandi."
            )
            break

    if not tamamlandi:
        print("Egitim tamamlanamadi: maksimum epoch sinirina ulasildi.")

    return beyin, gercek_epoch, toplam_geribildirim, tamamlandi


def sonuc_yazdir(yontem, beyin, egitim_oruntuleri, test_oruntuleri,
                 toplam_epoch, toplam_geribildirim, tamamlandi):
    egitim_dogrusu, egitim_sonuclari = degerlendir(
        beyin, egitim_oruntuleri
    )
    test_dogrusu, test_sonuclari = degerlendir(
        beyin, test_oruntuleri
    )

    print(f"\n{yontem} - EGITIM SONRASI DEGERLENDIRME")
    print("-" * 88)

    for etiket, sonuclar in (
        ("EGITIM", egitim_sonuclari),
        ("GORULMEMIS TEST", test_sonuclari),
    ):
        print(f"{etiket}:")
        for girdi, beklenen, cikti, dogru in sonuclar:
            print(
                f"  {girdi} -> beklenen {beklenen}, cikan {cikti}, "
                f"{'DOGRU' if dogru else 'YANLIS'}"
            )

    print(
        f"Toplam epoch: {toplam_epoch} | "
        f"Toplam geri bildirim: {toplam_geribildirim}"
    )
    print(
        f"Egitim basarisi: {egitim_dogrusu}/{len(egitim_oruntuleri)}"
    )
    print(
        f"Genelleme basarisi: {test_dogrusu}/{len(test_oruntuleri)}"
    )
    print(f"Ogretim kriteri tamamlandi mi: {'EVET' if tamamlandi else 'HAYIR'}")

    return {
        "egitim_dogrusu": egitim_dogrusu,
        "egitim_toplam": len(egitim_oruntuleri),
        "test_dogrusu": test_dogrusu,
        "test_toplam": len(test_oruntuleri),
        "epoch": toplam_epoch,
        "geribildirim": toplam_geribildirim,
        "tamamlandi": tamamlandi,
    }


def deneyi_calistir(egitim_sayisi):
    egitim_oruntuleri = TUM_ORUNTULER[:egitim_sayisi]
    test_oruntuleri = TUM_ORUNTULER[egitim_sayisi:] + [
        TESTTE_TUTULACAK_BIRLESIK,
        EK_TEST_POZITIF,
    ]

    # Tekrar yok; test kumesi egitim kumesinin tamlayicisidir.
    assert len(egitim_oruntuleri) == egitim_sayisi
    assert len(test_oruntuleri) == 8 - egitim_sayisi
    assert TESTTE_TUTULACAK_BIRLESIK in test_oruntuleri

    print("\n" + "=" * 88)
    print(f"ORNEKLEM DENEYI: {egitim_sayisi} EGITIM / "
          f"{len(test_oruntuleri)} TEST")
    print("=" * 88)
    print("Egitim oruntuleri:")
    for girdi, beklenen in egitim_oruntuleri:
        print(f"  {girdi} -> {beklenen}")
    print("Test oruntuleri (egitim boyunca kullanilmayacak):")
    for girdi, beklenen in test_oruntuleri:
        print(f"  {girdi} -> {beklenen}")

    # Iki yontem de ayni AG_SEED ile ayni baslangic mimarisinden baslar.
    artimli = artimli_ogretme(egitim_oruntuleri)
    karma = karma_ogretme(egitim_oruntuleri)

    artimli_sonuc = sonuc_yazdir(
        "ARTIMLI OGRETME",
        *artimli[:1],
        egitim_oruntuleri,
        test_oruntuleri,
        artimli[1],
        artimli[2],
        artimli[3],
    )
    karma_sonuc = sonuc_yazdir(
        "KARMA OGRETME",
        *karma[:1],
        egitim_oruntuleri,
        test_oruntuleri,
        karma[1],
        karma[2],
        karma[3],
    )

    print("\nYONTEM KARSILASTIRMASI")
    print("-" * 88)
    for ad, sonuc in (
        ("Artimli", artimli_sonuc),
        ("Karma", karma_sonuc),
    ):
        print(
            f"{ad:10s} | epoch={sonuc['epoch']:4d} | "
            f"egitim={sonuc['egitim_dogrusu']}/{sonuc['egitim_toplam']} | "
            f"test={sonuc['test_dogrusu']}/{sonuc['test_toplam']} | "
            f"feedback={sonuc['geribildirim']} | "
            f"kriter={'tamam' if sonuc['tamamlandi'] else 'tamamlanmadi'}"
        )


if __name__ == "__main__":
    deneyi_calistir(6)
    deneyi_calistir(5)
