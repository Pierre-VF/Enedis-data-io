if __name__ == "__main__":
    from datetime import date, timedelta

    from dotenv import load_dotenv
    from enedis_data_io.fr import ApiEntreprises

    load_dotenv()

    api = ApiEntreprises()

    c = api.compteurs()

    prm_1 = c[1]
    addr = api.adresse_du_compteur(prm=prm_1)

    start = date.today() - timedelta(days=31)
    end = start + timedelta(days=7)
    pj = api.production_journaliere(prm=prm_1, start=start, end=end)
    pdh = api.production_par_demi_heure(prm=prm_1, start=start, end=end)
    cj = api.consommation_journaliere(prm=prm_1, start=start, end=end)

    print(c)
