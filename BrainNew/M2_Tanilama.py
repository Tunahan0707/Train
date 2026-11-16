"""M2 ikili buyukluk deneyinin katman-katman pasif tanilamasi.

Karar katmaninda her nöronun membran girdisini ve her dendrite hangi ara
nörondan ne kadar elektriksel girdi geldigini ayri ayri raporlar.

Calistirma:
    python -m BrainNew.M2_Tanilama
"""
from collections import defaultdict
import json

from BrainNew.M2_BinaryBuyuklukKarsilastirma import (
    BinaryBuyuklukKarsilastirmaDeneyi,
)


def _katman_ozeti(kimlikler, biriken):
    noronlar = [biriken["noron"][kimlik] for kimlik in kimlikler]
    toplam_ateslenme = sum(k["ateslenme"] for k in noronlar)
    return {
        "noron_sayisi": len(noronlar),
        "ateslenme": toplam_ateslenme,
        "entegrasyon": sum(k["entegrasyon"] for k in noronlar),
        "toplam_isaretli_membran_girdisi": round(sum(k["isaretli_girdi"] for k in noronlar), 6),
        "toplam_mutlak_membran_girdisi": round(sum(k["mutlak_girdi"] for k in noronlar), 6),
        "maksimum_tek_entegrasyon_girdisi": round(max((k["maks_girdi"] for k in noronlar), default=0.0), 6),
        "gorulen_maksimum_membran": round(max((k["maks_membran"] for k in noronlar), default=0.0), 6),
        "gorulen_maksimum_esik_marji": round(max((k["maks_esik_marji"] for k in noronlar), default=0.0), 6),
        "noron_basina_ateslenme": round(toplam_ateslenme / len(noronlar), 4) if noronlar else 0.0,
    }


def _sinaps_ozeti(deney, grup, biriken):
    sinapslar = deney.duyusal_ara_sinapslari if grup == "reseptor->ara" else deney.ara_karar_sinapslari
    kayit = biriken["sinaps"][grup]
    katsayilar = [sinaps.iletim_etkisi() for sinaps in sinapslar]
    marjlar = [sinaps.potansiyel - sinaps.esik for sinaps in sinapslar]
    aktivasyon = kayit["aktivasyon"]
    return {
        "terminal_sayisi": len(sinapslar),
        "son_durum_esik_ustu_terminal": sum(x >= 0.0 for x in marjlar),
        "son_durum_potansiyel_esik_marji_min": round(min(marjlar, default=0.0), 6),
        "son_durum_potansiyel_esik_marji_maks": round(max(marjlar, default=0.0), 6),
        "toplam_aktivasyon": aktivasyon,
        "aktivasyon_basi_ortalama": round(aktivasyon / biriken["episode_sayisi"], 4) if biriken["episode_sayisi"] else 0.0,
        "pozitif_etkili_terminal": sum(x > 0 for x in katsayilar),
        "negatif_etkili_terminal": sum(x < 0 for x in katsayilar),
        "modulator_guncelleme": kayit["modulator_guncelleme"],
        "toplam_modulator_agirlik_degisim": round(kayit["modulator_agirlik_degisim"], 8),
    }


def tanilama_calistir(seed=20261121):
    deney = BinaryBuyuklukKarsilastirmaDeneyi(seed=seed)
    biriken = {
        "episode_sayisi": 0,
        "noron": defaultdict(lambda: {
            "ateslenme": 0, "ateslenilen_episode": 0, "entegrasyon": 0,
            "isaretli_girdi": 0.0, "mutlak_girdi": 0.0, "maks_girdi": 0.0,
            "maks_membran": float("-inf"), "maks_esik_marji": float("-inf"),
            "episode_maks_membran_toplami": 0.0,
            "episode_maks_esik_marji_toplami": 0.0,
        }),
        "dendrit": defaultdict(lambda: {
            "entegrasyon": 0, "isaretli_girdi": 0.0, "mutlak_girdi": 0.0,
            "maks_pozitif_girdi": 0.0, "maks_negatif_girdi": 0.0,
            "maks_mutlak_girdi": 0.0,
        }),
        "sinaps": defaultdict(lambda: {
            "aktivasyon": 0, "modulator_guncelleme": 0,
            "modulator_agirlik_degisim": 0.0,
        }),
    }
    onceki_ateslenmeler = {
        kimlik: noron.ateslenme_sayisi
        for kimlik, noron in deney.beyin.noronlar.items()
    }
    onceki_sinaps = {
        sinaps.kimlik: (sinaps.aktivasyon_sayisi, sinaps.modulator_guncelleme_sayisi, sinaps.toplam_modulator_agirlik_degisim)
        for sinaps in deney.sinapslar
    }

    sonuclar = []
    for sol, sag in deney.egitim_ornekleri:
        sonuclar.append(deney.episode_calistir(sol, sag, feedback=True))
        biriken["episode_sayisi"] += 1
        for kimlik, noron in deney.beyin.noronlar.items():
            kayit = biriken["noron"][kimlik]
            delta_ates = noron.ateslenme_sayisi - onceki_ateslenmeler[kimlik]
            kayit["ateslenme"] += delta_ates
            kayit["ateslenilen_episode"] += delta_ates > 0
            onceki_ateslenmeler[kimlik] = noron.ateslenme_sayisi
            kayit["entegrasyon"] += noron.tanilama_entegre_sayisi
            kayit["isaretli_girdi"] += noron.tanilama_toplam_membran_girdisi
            kayit["mutlak_girdi"] += noron.tanilama_mutlak_membran_girdisi
            kayit["maks_girdi"] = max(kayit["maks_girdi"], noron.tanilama_maksimum_membran_girdisi)
            kayit["maks_membran"] = max(kayit["maks_membran"], noron.tanilama_maksimum_membran)
            kayit["maks_esik_marji"] = max(kayit["maks_esik_marji"], noron.tanilama_maksimum_esik_marji)
            kayit["episode_maks_membran_toplami"] += noron.tanilama_maksimum_membran
            kayit["episode_maks_esik_marji_toplami"] += noron.tanilama_maksimum_esik_marji
            for dendrit_id, dendrit_kayit in noron.tanilama_dendrit_girdileri.items():
                hedef = biriken["dendrit"][(kimlik, dendrit_id)]
                for alan in hedef:
                    hedef[alan] += dendrit_kayit[alan]

        for sinaps in deney.sinapslar:
            eski_aktivasyon, eski_guncelleme, eski_delta = onceki_sinaps[sinaps.kimlik]
            grup = "reseptor->ara" if sinaps in deney.duyusal_ara_sinapslari else "ara->karar"
            kayit = biriken["sinaps"][grup]
            kayit["aktivasyon"] += sinaps.aktivasyon_sayisi - eski_aktivasyon
            kayit["modulator_guncelleme"] += sinaps.modulator_guncelleme_sayisi - eski_guncelleme
            kayit["modulator_agirlik_degisim"] += sinaps.toplam_modulator_agirlik_degisim - eski_delta
            onceki_sinaps[sinaps.kimlik] = (
                sinaps.aktivasyon_sayisi, sinaps.modulator_guncelleme_sayisi,
                sinaps.toplam_modulator_agirlik_degisim,
            )

    gruplar = {
        "reseptor": deney.duyusal_noronlari,
        "ara": deney.ara_noronlari,
        "karar": deney.KARAR_NORONLARI,
    }
    rapor = {
        "egitim": deney.ozetle(sonuclar),
        "katmanlar": {ad: _katman_ozeti(kimlikler, biriken) for ad, kimlikler in gruplar.items()},
        "sinapslar": {ad: _sinaps_ozeti(deney, ad, biriken) for ad in ("reseptor->ara", "ara->karar")},
        "karar_noronlari": {},
    }
    ara_kaynagi = {
        (sinaps.hedef.kimlik, sinaps.hedef_dendrit_id): sinaps.kaynak.kimlik
        for sinaps in deney.ara_karar_sinapslari
    }
    for kimlik in deney.KARAR_NORONLARI:
        kayit = biriken["noron"][kimlik]
        dendrit_raporu = {}
        for (hedef_id, dendrit_id), deger in biriken["dendrit"].items():
            if hedef_id == kimlik:
                kaynak_id = ara_kaynagi.get((kimlik, dendrit_id), dendrit_id)
                dendrit_raporu[kaynak_id] = {
                    "dendrit_id": dendrit_id,
                    "entegrasyon": deger["entegrasyon"],
                    "toplam_isaretli_girdi": round(deger["isaretli_girdi"], 6),
                    "toplam_mutlak_girdi": round(deger["mutlak_girdi"], 6),
                    "maksimum_pozitif_girdi": round(deger["maks_pozitif_girdi"], 6),
                    "maksimum_negatif_girdi": round(deger["maks_negatif_girdi"], 6),
                    "maksimum_mutlak_girdi": round(deger["maks_mutlak_girdi"], 6),
                }
        rapor["karar_noronlari"][kimlik] = {
            "ateslenme": kayit["ateslenme"],
            "ateslenilen_episode": kayit["ateslenilen_episode"],
            "toplam_episode": biriken["episode_sayisi"],
            "ortalama_episode_maksimum_membran": round(kayit["episode_maks_membran_toplami"] / biriken["episode_sayisi"], 6),
            "ortalama_episode_maksimum_esik_marji": round(kayit["episode_maks_esik_marji_toplami"] / biriken["episode_sayisi"], 6),
            "genel_maksimum_membran": round(kayit["maks_membran"], 6),
            "genel_maksimum_esik_marji": round(kayit["maks_esik_marji"], 6),
            "toplam_isaretli_membran_girdisi": round(kayit["isaretli_girdi"], 6),
            "toplam_mutlak_membran_girdisi": round(kayit["mutlak_girdi"], 6),
            "entegrasyon": kayit["entegrasyon"],
            "ara_noron_kaynaklari": dendrit_raporu,
        }
    return rapor


if __name__ == "__main__":
    print(json.dumps(tanilama_calistir(), ensure_ascii=False, indent=2))
