class ReseptorOrgan:
    """Görev girdilerini nöronlara duyusal olay olarak sunan ince arayüz."""

    def kodla(self, beyin, girdiler):
        """(noron_id, dendrit_id, etki, gecikme) kayıtlarını ağa yollar."""
        for noron_id, dendrit_id, etki, gecikme in girdiler:
            beyin.duyusal_girdi(
                noron_id, dendrit_id, etki, gecikme=gecikme
            )
