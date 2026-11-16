import math


GOREV_TURLERI = frozenset({"B1", "B2", "B3", "B4", "B5", "B6"})


class DeneyOrnegi:
    """Tek bir giriş dizisi ve beklenen nöral çıktılar."""

    def __init__(self, kimlik, girdiler, beklenen_ciktilar):
        if not isinstance(kimlik, str) or not kimlik:
            raise ValueError("Örnek kimliği boş olmayan metin olmalı.")

        temiz_girdiler = []
        for girdi in girdiler:
            if len(girdi) != 4:
                raise ValueError(
                    "Her girdi (noron_id, dendrit_id, etki, gecikme) olmalı."
                )
            noron_id, dendrit_id, etki, gecikme = girdi
            etki = float(etki)
            gecikme = float(gecikme)
            if not math.isfinite(etki):
                raise ValueError("Girdi etkisi sonlu olmalı.")
            if not math.isfinite(gecikme) or gecikme <= 0:
                raise ValueError("Girdi gecikmesi sonlu ve pozitif olmalı.")
            temiz_girdiler.append(
                (str(noron_id), str(dendrit_id), etki, gecikme)
            )

        ciktilar = frozenset(str(x) for x in beklenen_ciktilar)
        self.kimlik = kimlik
        self.girdiler = tuple(temiz_girdiler)
        self.beklenen_ciktilar = ciktilar


class DeneyGorevi:
    """Eğitim ve test örneklerini kimlik düzeyinde birbirinden ayırır."""

    def __init__(self, kimlik, tur, egitim, test):
        if not isinstance(kimlik, str) or not kimlik:
            raise ValueError("Görev kimliği boş olmayan metin olmalı.")
        if tur not in GOREV_TURLERI:
            raise ValueError(f"Bilinmeyen baseline görev türü: {tur}")

        egitim = tuple(egitim)
        test = tuple(test)
        tum_ornekler = egitim + test
        kimlikler = [ornek.kimlik for ornek in tum_ornekler]
        if len(kimlikler) != len(set(kimlikler)):
            raise ValueError("Eğitim ve test örnek kimlikleri benzersiz olmalı.")
        if not egitim or not test:
            raise ValueError("Eğitim ve test kümeleri ayrı ayrı boş olamaz.")

        self.kimlik = kimlik
        self.tur = tur
        self.egitim = egitim
        self.test = test


class DeneySurucusu:
    """
    Öğrenme yapmayan baseline yürütücüsü.

    Her örnek için ag_kurucu yeni ve bağımsız bir Beyin döndürmelidir.
    Yürütücü yalnızca duyusal girdileri planlar ve gözlenen ateşlenmeleri ölçer.
    """

    def __init__(self, ag_kurucu):
        if not callable(ag_kurucu):
            raise TypeError("ag_kurucu çağrılabilir olmalı.")
        self.ag_kurucu = ag_kurucu
        self._kullanilmis_aglar = []

    def ornegi_calistir(self, ornek):
        beyin = self.ag_kurucu()
        if not hasattr(beyin, "noronlar") or not hasattr(beyin, "duyusal_girdi"):
            raise TypeError("ag_kurucu bir Beyin örneği döndürmeli.")

        if any(beyin is onceki for onceki in self._kullanilmis_aglar):
            raise ValueError(
                "Her deney örneği için ag_kurucu yeni ve bağımsız bir Beyin döndürmeli."
            )
        self._kullanilmis_aglar.append(beyin)

        bilinmeyenler = (
            ornek.beklenen_ciktilar - set(beyin.noronlar)
        )
        if bilinmeyenler:
            raise ValueError(
                f"Beklenen çıktı nöronları ağda yok: {sorted(bilinmeyenler)}"
            )

        for noron_id, dendrit_id, etki, gecikme in ornek.girdiler:
            beyin.duyusal_girdi(
                noron_id, dendrit_id, etki, gecikme=gecikme
            )

        islenen_olay = beyin.calistir()
        gerceklesen = frozenset(
            noron_id
            for noron_id, noron in beyin.noronlar.items()
            if noron.ateslenme_sayisi > 0
        )

        return {
            "ornek": ornek.kimlik,
            "beklenen": tuple(sorted(ornek.beklenen_ciktilar)),
            "gerceklesen": tuple(sorted(gerceklesen)),
            "dogru": gerceklesen == ornek.beklenen_ciktilar,
            "islenen_olay": islenen_olay,
            "simulasyon_zamani": beyin.zaman,
        }

    def gorevi_degerlendir(self, gorev, bolum="test"):
        if bolum not in ("egitim", "test"):
            raise ValueError("Bölüm 'egitim' veya 'test' olmalı.")

        ornekler = gorev.egitim if bolum == "egitim" else gorev.test
        sonuclar = [self.ornegi_calistir(ornek) for ornek in ornekler]
        dogru = sum(sonuc["dogru"] for sonuc in sonuclar)

        tp = fp = fn = 0
        for sonuc in sonuclar:
            beklenen = set(sonuc["beklenen"])
            gerceklesen = set(sonuc["gerceklesen"])
            tp += len(beklenen & gerceklesen)
            fp += len(gerceklesen - beklenen)
            fn += len(beklenen - gerceklesen)

        toplam = len(sonuclar)
        return {
            "gorev": gorev.kimlik,
            "tur": gorev.tur,
            "bolum": bolum,
            "ornek_sayisi": toplam,
            "tam_eslesme": dogru,
            "tam_eslesme_orani": dogru / toplam,
            "dogru_pozitif": tp,
            "yanlis_pozitif": fp,
            "yanlis_negatif": fn,
            "islenen_olay": sum(s["islenen_olay"] for s in sonuclar),
            "ornek_sonuclari": tuple(sonuclar),
        }

    def gorevi_calistir(self, gorev):
        """Eğitim ve test ölçümlerini ayrı raporlar; ağı değiştirmez."""
        return {
            "gorev": gorev.kimlik,
            "tur": gorev.tur,
            "egitim": self.gorevi_degerlendir(gorev, "egitim"),
            "test": self.gorevi_degerlendir(gorev, "test"),
        }
