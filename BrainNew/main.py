from BrainNew.Baglanti import Baglanti
from BrainNew.Beyin import Beyin
from BrainNew.Dendrid import Dendrid
from BrainNew.KimyasalAlan import KimyasalAlan
from BrainNew.Noron import Noron


def prototipi_calistir():
    kimyasal_alan = KimyasalAlan()
    beyin = Beyin(kimyasal_alan)

    kaynak = Noron("kaynak", konum=(0.0, 0.0))
    hedef = Noron("hedef", konum=(1.0, 0.0))

    kaynak_dendrit = Dendrid("kaynak_giris", konum=(0.0, 0.0))
    hedef_dendrit = Dendrid("hedef_giris", konum=(1.0, 0.0))
    hedef_dendrit.transmitter_duyarliligi_ayarla("uyarici", 0.8)
    hedef_dendrit.transmitter_duyarliligi_ayarla("modulator", 0.4)

    cikis = Baglanti(
        "kaynak_hedef",
        kaynak,
        hedef,
        uzunluk=1.0,
        iletim_hizi=1.0,
        esik=0.2,
        hedef_dendrit_id="hedef_giris",
        etki=50.0,
        terminal_konumu=(0.5, 0.0),
        transmitter_profili={"uyarici": 2.0, "modulator": 0.5},
        kimyasal_yayilim=1.0,
        kimyasal_temizlenme=0.1,
    )

    kaynak_dendrit.sinaps_bagla(cikis, 1.0)
    kaynak.dendrit_ekle(kaynak_dendrit)
    kaynak.cikis_sinapsi_ekle(cikis)
    hedef.dendrit_ekle(hedef_dendrit)

    beyin.noron_ekle(kaynak)
    beyin.noron_ekle(hedef)
    beyin.duyusal_girdi("kaynak", "kaynak_giris", 100.0)

    islenen_olay = beyin.calistir()

    print("BrainNew ilk prototip")
    print(f"İşlenen olay: {islenen_olay}")
    print(f"Kaynak nöron ateşlenmesi: {kaynak.ateslenme_sayisi}")
    print(f"Hedef nöron ateşlenmesi: {hedef.ateslenme_sayisi}")
    print(f"Çıkış sinapsı aktivasyonu: {cikis.aktivasyon_sayisi}")
    print(
        "Hedefte uyarıcı yoğunluğu: "
        f"{kimyasal_alan.yogunluk('uyarici', hedef_dendrit.konum, beyin.zaman):.6f}"
    )
    print(
        "Hedefte modülatör yoğunluğu: "
        f"{kimyasal_alan.yogunluk('modulator', hedef_dendrit.konum, beyin.zaman):.6f}"
    )


if __name__ == "__main__":
    prototipi_calistir()
