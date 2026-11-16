"""M2 ikili buyukluk deneyinin katman-katman pasif tanilamasi.

Calistirma:
    python -m BrainNew.M2_Tanilama
"""
from collections import defaultdict
import json

from BrainNew.M2_BinaryBuyuklukKarsilastirma import (
    BinaryBuyuklukKarsilastirmaDeneyi,
)


def _katman_ozeti(deney, kimlikler, biriken):
    noronlar = [deney.beyin.noronlar[kimlik] for kimlik in kimlikler]
    kayit = biriken["noron"][tuple(kimlikler)]
    sayisal_maksimum = lambda deger: (
        round(deger, 6) if deger != float("-inf") else None
    )
    return {
        "noron_sayisi": len(noronlar),
        "ateslenme": kayit["ateslenme"],
        "entegrasyon": kayit["entegrasyon"],
        "toplam_isaretli_membran_girdisi": round(kayit["isaretli_girdi"], 6),
        "toplam_mutlak_membran_girdisi": round(kayit["mutlak_girdi"], 6),
        "maksimum_tek_entegrasyon_girdisi": round(kayit["maks_girdi"], 6),
        "gorulen_maksimum_membran": sayisal_maksimum(kayit["maks_membran"]),
        "gorulen_maksimum_esik_marji": sayisal_maksimum(kayit["maks_esik_marji"]),
        "noron_basina_ateslenme": round(
            kayit["ateslenme"] / len(noronlar), 4
        ) if noronlar else 0.0,
    }


def tanilama_calistir(seed=20261121):
    deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=seed)
    biriken = {
        "noron": defaultdict(lambda: {
            "ateslenme": 0,
            "entegrasyon": 0,
            "isaretli_girdi": 0.0,
            "mutlak_girdi": 0.0,
            "maks_girdi": 0.0,
            "maks_membran": float("-inf"),
            "maks_esik_marji": float("-inf"),
        }),
        "sinaps": defaultdict(lambda: {
            "aktivasyon": 0,
            "modulator_guncelleme": 0,
            "modulator_agirlik_degisim": 0.0,
        }),
    }

    onceki_ateslenmeler = {
        kimlik: noron.ateslenme_sayisi
        for kimlik, noron in deney.beyin.noronlar.items()
    }
    onceki_sinaps = {
        sinaps.kimlik: (
            sinaps.aktivasyon_sayisi,
            sinaps.modulator_guncelleme_sayisi,
            sinaps.toplam_modulator_agirlik_degisim,
        )
        for sinaps in deney.sinapslar
    }

    sonuclar = []
    for sol, sag in deney.egitim_ornekleri:
        sonuclar.append(deney.episode_calistir(sol, sag, feedback=True))

        for kimlik, noron in deney.beyin.noronlar.items():
            kayit = biriken["noron"][tuple(
                (deney.sol_girdi_noronu, deney.sag_girdi_noronu)
                if kimlik in deney.duyusal_noronlari
                else deney.ara_noronlari
                if kimlik in deney.ara_noronlari
                else deney.KARAR_NORONLARI
            )]
            kayit["ateslenme"] += (
                noron.ateslenme_sayisi - onceki_ateslenmeler[kimlik]
            )
            onceki_ateslenmeler[kimlik] = noron.ateslenme_sayisi
            kayit["entegrasyon"] += noron.tanilama_entegre_sayisi
            kayit["isaretli_girdi"] += noron.tanilama_toplam_membran_girdisi
            kayit["mutlak_girdi"] += noron.tanilama_mutlak_membran_girdisi
            kayit["maks_girdi"] = max(
                kayit["maks_girdi"], noron.tanilama_maksimum_membran_girdisi
            )
            kayit["maks_membran"] = max(
                kayit["maks_membran"], noron.tanilama_maksimum_membran
            )
            kayit["maks_esik_marji"] = max(
                kayit["maks_esik_marji"],
                noron.tanilama_maksimum_esik_marji,
            )

        for sinaps in deney.sinapslar:
            eski_aktivasyon, eski_guncelleme, eski_delta = onceki_sinaps[
                sinaps.kimlik
            ]
            kayit = biriken["sinaps"][
                "reseptor->ara"
                if sinaps in deney.duyusal_ara_sinapslari
                else "ara->karar"
            ]
            kayit["aktivasyon"] += sinaps.aktivasyon_sayisi - eski_aktivasyon
            kayit["modulator_guncelleme"] += (
                sinaps.modulator_guncelleme_sayisi - eski_guncelleme
            )
            kayit["modulator_agirlik_degisim"] += (
                sinaps.toplam_modulator_agirlik_degisim - eski_delta
            )
            onceki_sinaps[sinaps.kimlik] = (
                sinaps.aktivasyon_sayisi,
                sinaps.modulator_guncelleme_sayisi,
                sinaps.toplam_modulator_agirlik_degisim,
            )

    gruplar = {
        "reseptor": deney.duyusal_noronlari,
        "ara": deney.ara_noronlari,
        "karar": deney.KARAR_NORONLARI,
    }
    rapor = {
        "egitim": deney.ozetle(sonuclar),
        "katmanlar": {
            ad: _katman_ozeti(deney, kimlikler, biriken)
            for ad, kimlikler in gruplar.items()
        },
        "sinapslar": {},
        "karar_noronlari": {},
    }

    for ad, sinapslar in (
        ("reseptor->ara", deney.duyusal_ara_sinapslari),
        ("ara->karar", deney.ara_karar_sinapslari),
    ):
        aktivasyon = biriken["sinaps"][ad]["aktivasyon"]
        katsayilar = [sinaps.iletim_etkisi() for sinaps in sinapslar]
        potansiyel_marjlari = [
            sinaps.potansiyel - sinaps.esik for sinaps in sinapslar
        ]
        rapor["sinapslar"][ad] = {
            "terminal_sayisi": len(sinapslar),
            "son_durum_esik_ustu_terminal": sum(x >= 0.0 for x in potansiyel_marjlari),
            "son_durum_potansiyel_esik_marji_min": round(
                min(potansiyel_marjlari, default=0.0), 6
            ),
            "son_durum_potansiyel_esik_marji_maks": round(
                max(potansiyel_marjlari, default=0.0), 6
            ),
            "toplam_aktivasyon": aktivasyon,
            "aktivasyon_basi_ortalama": round(
                aktivasyon / len(sonuclar), 4
            ) if sonuclar else 0.0,
            "pozitif_etkili_terminal": sum(x > 0 for x in katsayilar),
            "negatif_etkili_terminal": sum(x < 0 for x in katsayilar),
            "modulator_guncelleme": biriken["sinaps"][ad][
                "modulator_guncelleme"
            ],
            "toplam_modulator_agirlik_degisim": round(
                biriken["sinaps"][ad]["modulator_agirlik_degisim"], 8
            ),
        }

    for kimlik in deney.KARAR_NORONLARI:
        noron = deney.beyin.noronlar[kimlik]
        rapor["karar_noronlari"][kimlik] = {
            "ateslenme": noron.ateslenme_sayisi,
            "son_membran": round(noron.membran, 6),
            "son_esik": round(noron.esik, 6),
            "son_episode_maksimum_membran": round(
                noron.tanilama_maksimum_membran, 6
            ),
            "son_episode_maksimum_esik_marji": round(
                noron.tanilama_maksimum_esik_marji, 6
            ),
        }

    return rapor


if __name__ == "__main__":
    print(json.dumps(tanilama_calistir(), ensure_ascii=False, indent=2))
