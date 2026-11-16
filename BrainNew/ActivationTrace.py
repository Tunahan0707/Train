"""Pasif aktivasyon ve nedensel yol tanılaması.

Bu sınıf yalnızca gözlem yapar. Sinaptik ağırlık, eşik, potansiyel veya
öğrenme kararı üzerinde değişiklik yapmaz. Beyin tarafından isteğe bağlı
bir gözlemci olarak kullanılır.
"""


class ActivationTrace:
    def __init__(self):
        self.olaylar = []
        self.ateslenmeler = []
        self.sinaps_aktivasyonlari = []
        self._bekleyen_iletim_izleri = {}
        self._sira = 0

    @classmethod
    def _ozetle(cls, deger):
        if deger is None or isinstance(deger, (str, int, bool, float)):
            return deger
        kimlik = getattr(deger, "kimlik", None)
        if kimlik is not None:
            return {"kimlik": str(kimlik), "tip": type(deger).__name__}
        if isinstance(deger, tuple):
            return tuple(cls._ozetle(x) for x in deger)
        if isinstance(deger, list):
            return tuple(cls._ozetle(x) for x in deger)
        if isinstance(deger, (set, frozenset)):
            return tuple(sorted(
                (cls._ozetle(x) for x in deger), key=repr
            ))
        if isinstance(deger, dict):
            return {
                str(k): cls._ozetle(v)
                for k, v in sorted(deger.items(), key=lambda item: str(item[0]))
            }
        raise TypeError(
            f"Aktivasyon izi desteklenmeyen veri türünü alamaz: "
            f"{type(deger).__name__}"
        )

    def _yeni_sira(self):
        sira = self._sira
        self._sira += 1
        return sira

    def olay_kaydet(self, zaman, olay_id, tur, hedef_id, veri=None):
        """Beyin olay kuyruğundan çıkan olayı değişmez bir özet olarak kaydeder."""
        kayit = {
            "kayit_turu": "olay",
            "sira": self._yeni_sira(),
            "zaman": float(zaman),
            "olay_id": int(olay_id),
            "olay_turu": str(tur),
            "hedef_id": str(hedef_id),
            "veri": self._ozetle(veri),
        }
        if tur == "sinaptik_girdi" and isinstance(veri, (tuple, list)) and veri:
            sinaps = veri[0]
            kayit["sinaps_id"] = getattr(sinaps, "kimlik", None)
            kayit["kaynak_aktivasyon_sira"] = (
                self._bekleyen_iletim_izleri.pop(int(olay_id), None)
            )
        self.olaylar.append(kayit)

    def iletim_olayi_planlandi(self, olay_id, aktivasyon_sira):
        """Gecikmeli hedef girdisini onu oluşturan terminal aktivasyonuna bağlar."""
        if aktivasyon_sira is not None:
            self._bekleyen_iletim_izleri[int(olay_id)] = int(aktivasyon_sira)

    def noron_ateslenmesini_kaydet(
        self, zaman, olay_id, noron, aktif_sinapslar
    ):
        """Ateşlenmenin nedensel girdilerini ve seçilmiş çıkışlarını kaydeder."""
        girdiler = sorted(
            str(s.kimlik) for s in noron._son_nedensel_girdi_sinapslari
        )
        ciktilar = sorted(str(s.kimlik) for s, _ in aktif_sinapslar)
        self.ateslenmeler.append({
            "kayit_turu": "noron_ateslenmesi",
            "sira": self._yeni_sira(),
            "zaman": float(zaman),
            "olay_id": int(olay_id),
            "noron_id": str(noron.kimlik),
            "girdi_sinapslari": tuple(girdiler),
            "aktif_cikis_sinapslari": tuple(ciktilar),
            "membran": float(noron.membran),
            "esik": float(noron.esik),
        })

    def sinaps_aktivasyonunu_kaydet(
        self, zaman, olay_id, sinaps, gecikme
    ):
        """Gerçekten aktive edilen terminalin anlık durumunu kaydeder."""
        kaynak = getattr(sinaps, "kaynak", None)
        hedef = getattr(sinaps, "hedef", None)
        sira = self._yeni_sira()
        self.sinaps_aktivasyonlari.append({
            "kayit_turu": "sinaps_aktivasyonu",
            "sira": sira,
            "zaman": float(zaman),
            "olay_id": olay_id,
            "sinaps_id": str(sinaps.kimlik),
            "kaynak_noron": str(kaynak.kimlik) if kaynak is not None else None,
            "hedef_noron": str(hedef.kimlik) if hedef is not None else None,
            "hedef_dendrit_id": getattr(sinaps, "hedef_dendrit_id", None),
            "gecikme": float(gecikme),
            "potansiyel": float(sinaps.potansiyel),
            "esik": float(sinaps.esik),
            "sinaptik_agirlik": float(sinaps.sinaptik_agirlik),
            "iletim_etkisi": float(sinaps.iletim_etkisi()),
            "yapisal_olgunluk": float(sinaps.yapisal_olgunluk),
        })
        return sira

    def nedensel_yol(self, hedef_noron_id, max_derinlik=32):
        """Son ateşlenmeye giden izlenebilir sinaptik yolu kronolojik döndürür.

        Yalnızca bu izleyicide gözlenmiş olayları kullanır. Kayıt dışı olaylar,
        izleyici başlatılmadan önceki geçmiş veya eksik nedensel bilgiler
        yeniden oluşturulamaz.
        """
        if not isinstance(max_derinlik, int) or max_derinlik < 1:
            raise ValueError("max_derinlik pozitif bir tam sayı olmalı.")

        ateslenmeler = {}
        for kayit in self.ateslenmeler:
            ateslenmeler.setdefault(kayit["noron_id"], []).append(kayit)

        aktivasyonlar = {}
        for kayit in self.sinaps_aktivasyonlari:
            aktivasyonlar.setdefault(kayit["sinaps_id"], []).append(kayit)

        ziyaret = set()
        secilen = {}

        def en_yakin_ateslenme(noron_id, zaman):
            adaylar = [
                kayit for kayit in ateslenmeler.get(noron_id, ())
                if kayit["zaman"] <= zaman
            ]
            return max(adaylar, key=lambda x: (x["zaman"], x["sira"])) if adaylar else None

        def duyusal_koku_ekle(noron_id, zaman):
            adaylar = [
                kayit for kayit in self.olaylar
                if kayit["olay_turu"] == "duyusal_girdi"
                and kayit["hedef_id"] == noron_id
                and kayit["zaman"] <= zaman
            ]
            if adaylar:
                kayit = max(adaylar, key=lambda x: (x["zaman"], x["sira"]))
                secilen[kayit["sira"]] = kayit

        def izle(ateslenme, derinlik):
            anahtar = ateslenme["sira"]
            if anahtar in ziyaret:
                return
            ziyaret.add(anahtar)
            secilen[anahtar] = ateslenme

            if derinlik >= max_derinlik:
                return

            girdi_sinapslari = ateslenme["girdi_sinapslari"]
            if not girdi_sinapslari:
                duyusal_koku_ekle(ateslenme["noron_id"], ateslenme["zaman"])
                return

            for sinaps_id in girdi_sinapslari:
                varislar = [
                    kayit for kayit in self.olaylar
                    if kayit["olay_turu"] == "sinaptik_girdi"
                    and kayit["hedef_id"] == ateslenme["noron_id"]
                    and kayit.get("sinaps_id") == sinaps_id
                    and kayit["zaman"] <= ateslenme["zaman"]
                ]
                if not varislar:
                    continue
                varis = max(varislar, key=lambda x: (x["zaman"], x["sira"]))
                secilen[varis["sira"]] = varis
                aktivasyon_sira = varis.get("kaynak_aktivasyon_sira")
                aktivasyon = next(
                    (
                        kayit for kayit in aktivasyonlar.get(sinaps_id, ())
                        if kayit["sira"] == aktivasyon_sira
                    ),
                    None,
                )
                if aktivasyon is None:
                    continue
                secilen[aktivasyon["sira"]] = aktivasyon
                kaynak_id = aktivasyon["kaynak_noron"]
                if kaynak_id is None:
                    continue
                kaynak_ateslenmesi = en_yakin_ateslenme(
                    kaynak_id, aktivasyon["zaman"]
                )
                if kaynak_ateslenmesi is None:
                    duyusal_koku_ekle(kaynak_id, aktivasyon["zaman"])
                else:
                    izle(kaynak_ateslenmesi, derinlik + 1)

        hedef = str(hedef_noron_id)
        son = en_yakin_ateslenme(hedef, float("inf"))
        if son is None:
            return tuple()
        izle(son, 0)
        return tuple(
            dict(kayit)
            for kayit in sorted(secilen.values(), key=lambda x: x["sira"])
        )

    def ozet(self):
        return {
            "olay_sayisi": len(self.olaylar),
            "noron_ateslenmesi": len(self.ateslenmeler),
            "sinaps_aktivasyonu": len(self.sinaps_aktivasyonlari),
        }

    def temizle(self):
        self.olaylar.clear()
        self.ateslenmeler.clear()
        self.sinaps_aktivasyonlari.clear()
        self._bekleyen_iletim_izleri.clear()
        self._sira = 0
