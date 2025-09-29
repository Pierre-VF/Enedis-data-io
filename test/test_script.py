if __name__ == "__main__":
    from enedis_data_io.fr import ApiEntreprises

    api = ApiEntreprises()

    c = api.compteurs()
    print(c)
