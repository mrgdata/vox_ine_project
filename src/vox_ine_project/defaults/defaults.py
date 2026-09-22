VAR_CAT_BOOL = False
VAR_PV_BOOL = False
VAR_ELECTORAL_YEAR_CHOSEN = 2023
VAR_LANGUAGE = "en"  # "en" or "es"

TUPLE_CAT_PROVINCES = ("08", "17", "25", "43")
TUPLE_PV_PROVINCES = ("01", "20", "48")

DIR_DATA = "./assets/data/"
DIR_PLOTS = "./assets/plots/"
FILE_1 = "INE_30824"
FILE_2 = "INE_30832"
FILE_3 = "INE_66593"
FILE_4 = "congreso19" if VAR_ELECTORAL_YEAR_CHOSEN == 2019 else "congreso23"
EXTENSION = ".csv"
SEPARATOR = ";"

DICT_DISTRIBUTION_INCOME = {
    "decile": 10,
    "ventile": 20,
    "quantile": 25,
    "centile": 100,
}

DICT_HEATMAP = {
    "PP": ["Blues", {"en": "Popular Party", "es": "Partido Popular"}],
    "Right": [
        "Blues",
        {
            "en": "Right-Wing parties (excl. VOX)",
            "es": "Partidos de derecha (excl. VOX)",
        },
    ],
    "Left": ["Oranges", {"en": "Left-Wing parties", "es": "Partidos de izquierda"}],
    "Non-nationalist Left": [
        "Reds",
        {
            "en": "Non-nationalist Left-Wing parties",
            "es": "Partidos de izquierda no nacionalistas",
        },
    ],
    "Nationalist Left": [
        "Oranges",
        {
            "en": "Nationalist Left-Wing parties",
            "es": "Partidos de izquierda nacionalistas",
        },
    ],
    "Nationalist Right": [
        "Greens",
        {
            "en": "Nationalist Right-Wing parties",
            "es": "Partidos de derecha nacionalistas",
        },
    ],
    "Non-nationalist Right": [
        "Blues",
        {
            "en": "Non-nationalist Right-Wing parties",
            "es": "Partidos de derecha no nacionalistas",
        },
    ],
    "PSOE": ["Reds", {"en": "Socialist Party", "es": "Partido Socialista"}],
    "SUMAR": ["Oranges", {"en": "SUMAR", "es": "SUMAR"}],
    "VOX": ["Greens", {"en": "VOX", "es": "VOX"}],
    "Other": ["Purples", {"en": "Non-aligned parties", "es": "Partidos no alineados"}],
    "population_share": ["PuBuGn", {"en": "population", "es": "población"}],
}

# bin name per n_bins, used to label heatmap axes (e.g. Quartile, Decile...)
DICT_BIN_NAMES = {
    2: {"en": "Half", "es": "Mitad"},
    3: {"en": "Tertile", "es": "Tercile"},
    4: {"en": "Quartile", "es": "Cuartile"},
    5: {"en": "Quintile", "es": "Quintile"},
    10: {"en": "Decile", "es": "Decile"},
    20: {"en": "Ventile", "es": "Ventile"},
    25: {"en": "Quantile", "es": "Cuantile"},
    100: {"en": "Percentile", "es": "Percentile"},
}
DICT_BIN_NAME_DEFAULT = {"en": "Group", "es": "Grupo"}

DICT_HEATMAP_LABELS = {
    "en": {
        "xlabel": "Percentage of Immigrant Population ({bin_name}s)",
        "ylabel": "Household Net Income ({bin_name}s)",
        "title": "{var_label} by Income × Immigration",
        "cbar_label": "{var_label}",
    },
    "es": {
        "xlabel": "Porcentaje de Población Inmigrante ({bin_name}s)",
        "ylabel": "Renta Neta Media del Hogar ({bin_name}s)",
        "title": "{var_label} por Renta × Inmigración",
        "cbar_label": "{var_label}",
    },
}


DICT_PARTY_IDEOLOGY_23_LEFT_RIGHT_NAT = {
    # NATIONALIST LEFT (peripheral/regional nationalist or independentist, left-leaning)
    "SUMAR MÉS": "Nationalist Left",
    "NUEVA CANARIAS - BLOQUE CANARISTA": "Nationalist Left",
    "AHORA CANARIAS-PARTIDO COMUNISTA DEL PUEBLO CANARIO": "Nationalist Left",
    "ESQUERRA REPUBLICANA DE CATALUNYA": "Nationalist Left",
    "CANDIDATURA D'UNITAT POPULAR-PER LA RUPTURA": "Nationalist Left",
    "BLOQUE NACIONALISTA GALEGO": "Nationalist Left",
    "EUSKAL HERRIA BILDU": "Nationalist Left",
    "COMPROMÍS - SUMAR: SUMEM PER GUANYAR": "Nationalist Left",
    # NATIONALIST RIGHT (peripheral/regional nationalist, right-leaning)
    "PARTIT DEMÒCRATA EUROPEU CATALÀ-ESPAI CIU": "Nationalist Right",
    "JUNTS PER CATALUNYA - JUNTS": "Nationalist Right",
    "EUZKO ALDERDI JELTZALEA-PARTIDO NACIONALISTA VASCO": "Nationalist Right",
    # NON-NATIONALIST LEFT (state-wide, non-independentist left)
    "FRENTE OBRERO": "Non-nationalist Left",
    "PARTIDO SOCIALISTA OBRERO ESPAÑOL": "Non-nationalist Left",
    "POR UN MUNDO MÁS JUSTO": "Non-nationalist Left",
    "PARTIDO ANIMALISTA CON EL MEDIO AMBIENTE": "Non-nationalist Left",
    "RECORTES CERO": "Non-nationalist Left",
    "SUMAR ANDALUCÍA": "Non-nationalist Left",
    "ADELANTE ANDALUCÍA": "Non-nationalist Left",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA": "Non-nationalist Left",
    "SUMAR": "Non-nationalist Left",
    "PARTIDO SOCIALISTA DE ISLAS BALEARES-PSOE": "Non-nationalist Left",
    "SUMAR CANARIAS": "Non-nationalist Left",
    "SUMAR ARAGÓN": "Non-nationalist Left",
    "PARTIT DELS SOCIALISTES DE CATALUNYA (PSC-PSOE)": "Non-nationalist Left",
    "SUMAR - EN COMÚ PODEM": "Non-nationalist Left",
    "PARTIT COMUNISTA DELS TREBALLADORS DE CATALUNYA": "Non-nationalist Left",
    "PARTIT ANIMALISTA AMB EL MEDI AMBIENT": "Non-nationalist Left",
    "PARTIDO DOS SOCIALISTAS DE GALICIA-PSOE": "Non-nationalist Left",
    "SUMAR GALICIA": "Non-nationalist Left",
    "POR UN MUNDO MAIS XUSTO": "Non-nationalist Left",
    "PARTIDO COMUNISTA DOS TRABALLADORES DE GALIZA": "Non-nationalist Left",
    "PARTIDO HUMANISTA": "Non-nationalist Left",
    "PARTIDO SOCIALISTA DE NAVARRA-PSOE": "Non-nationalist Left",
    "PARTIDO SOCIALISTA DE EUSKADI-EUSKADIKO EZKERRA (PSOE)": "Non-nationalist Left",
    "BIDEZKO MUNDURANTZ": "Non-nationalist Left",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE EUSKADI/EUSKADIKO LANGILEEN ALDERDI KOMUNISTA": "Non-nationalist Left",
    # NON-NATIONALIST RIGHT (state-wide / unionist right)
    "PARTIDO POPULAR": "Non-nationalist Right",
    "PARTIDO POPULAR / PARTIT POPULAR": "Non-nationalist Right",
    "PARTIT POPULAR / PARTIDO POPULAR": "Non-nationalist Right",
    "VOX": "Non-nationalist Right",
    "FALANGE ESPAÑOLA DE LAS J.O.N.S.": "Non-nationalist Right",
    "PARTIDO UNIONISTA ESTADO DE ESPAÑA": "Non-nationalist Right",
    "UNION DEL PUEBLO NAVARRO": "Non-nationalist Right",
    "COALICIÓN DE CENTRO DEMOCRÁTICO": "Non-nationalist Right",
    # OTHER (regionalist non-nationalist, single-issue, protest, blank, centrist, unclear)
    "ALMERIENSES - REGIONALISTAS PRO ALMERÍA": "Other",
    "LIBRES": "Other",
    "CAMINANDO JUNTOS": "Other",
    "ESCAÑOS EN BLANCO PARA DEJAR ESCAÑOS VACÍOS": "Other",
    "JUNTOS POR GRANADA": "Other",
    "POR HUELVA": "Other",
    "JAÉN MERECE MÁS": "Other",
    "FEDERACIÓN DE LOS INDEPENDIENTES DE ARAGÓN": "Other",
    "ARAGÓN EXISTE - COALICIÓN EXISTE": "Other",
    "PARTIDO ARAGONÉS": "Other",
    "TERUEL EXISTE - COALICIÓN EXISTE": "Other",
    "ASTURIAS EXISTE-ESPAÑA VACIADA": "Other",
    "COALICIÓN CANARIA": "Other",
    "POR ÁVILA": "Other",
    "VÍA BURGALESA": "Other",
    "ESPAÑA VACIADA-PARTIDO CASTELLANO-TIERRA COMUNERA": "Other",
    "ESPAÑA VACIADA": "Other",
    "PARTIDO REGIONALISTA DEL PAÍS LEONÉS": "Other",
    "UNIÓN DEL PUEBLO LEONÉS": "Other",
    "VAMOS PALENCIA": "Other",
    "GRUPO INDEPENDIENTE PALENCIA TIERRA VIVA": "Other",
    "TERCERA EDAD EN ACCIÓN": "Other",
    "SORIA ¡YA!": "Other",
    "UNIDAD CASTELLANA": "Other",
    "FUERZA CÍVICA": "Other",
    "ZAMORA SÍ": "Other",
    "ESCONS EN BLANC": "Other",
    "ENTRE VEÏNS CATALUNYA": "Other",
    "UNIDOS POR LA SOLIDARIDAD INTERNACIONAL": "Other",
    "BLOQUE EXTREMEÑO": "Other",
    "SOMOS CÁCERES": "Other",
    "GEROA BAI": "Other",
    "REFERÉNDUM SISTEMA DINERO": "Other",
    "POR MI REGIÓN": "Other",
    "PARTIDO AUTÓNOMOS": "Other",
    "ESTAT VALENCIÀ DEL BENESTAR": "Other",
    "COALICIÓN POR MELILLA": "Other",
}

DICT_PARTY_IDEOLOGY_23_MAIN_PARTIES = {
    # PSOE and regional branches
    "PARTIDO SOCIALISTA OBRERO ESPAÑOL": "PSOE",
    "PARTIDO SOCIALISTA DE ISLAS BALEARES-PSOE": "PSOE",
    "PARTIT DELS SOCIALISTES DE CATALUNYA (PSC-PSOE)": "PSOE",
    "PARTIDO DOS SOCIALISTAS DE GALICIA-PSOE": "PSOE",
    "PARTIDO SOCIALISTA DE NAVARRA-PSOE": "PSOE",
    "PARTIDO SOCIALISTA DE EUSKADI-EUSKADIKO EZKERRA (PSOE)": "PSOE",
    # PP and joint lists
    "PARTIDO POPULAR": "PP",
    "PARTIDO POPULAR / PARTIT POPULAR": "PP",
    "PARTIT POPULAR / PARTIDO POPULAR": "PP",
    # VOX
    "VOX": "VOX",
    # SUMAR and coalition partners/relatives
    "SUMAR": "SUMAR",
    "SUMAR ANDALUCÍA": "SUMAR",
    "SUMAR MÉS": "SUMAR",
    "SUMAR CANARIAS": "SUMAR",
    "SUMAR GALICIA": "SUMAR",
    "SUMAR ARAGÓN": "SUMAR",
    "SUMAR - EN COMÚ PODEM": "SUMAR",
    "COMPROMÍS - SUMAR: SUMEM PER GUANYAR": "SUMAR",
    "ADELANTE ANDALUCÍA": "SUMAR",
    # OTHER (remaining nationalist parties, minor parties, regionalist, single-issue, protest, blank, unclear)
    "FRENTE OBRERO": "Other",
    "POR UN MUNDO MÁS JUSTO": "Other",
    "PARTIDO ANIMALISTA CON EL MEDIO AMBIENTE": "Other",
    "RECORTES CERO": "Other",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA": "Other",
    "NUEVA CANARIAS - BLOQUE CANARISTA": "Other",
    "AHORA CANARIAS-PARTIDO COMUNISTA DEL PUEBLO CANARIO": "Other",
    "ESQUERRA REPUBLICANA DE CATALUNYA": "Other",
    "CANDIDATURA D'UNITAT POPULAR-PER LA RUPTURA": "Other",
    "PARTIT COMUNISTA DELS TREBALLADORS DE CATALUNYA": "Other",
    "PARTIT ANIMALISTA AMB EL MEDI AMBIENT": "Other",
    "BLOQUE NACIONALISTA GALEGO": "Other",
    "POR UN MUNDO MAIS XUSTO": "Other",
    "PARTIDO COMUNISTA DOS TRABALLADORES DE GALIZA": "Other",
    "PARTIDO HUMANISTA": "Other",
    "EUSKAL HERRIA BILDU": "Other",
    "BIDEZKO MUNDURANTZ": "Other",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE EUSKADI/EUSKADIKO LANGILEEN ALDERDI KOMUNISTA": "Other",
    "FALANGE ESPAÑOLA DE LAS J.O.N.S.": "Other",
    "PARTIDO UNIONISTA ESTADO DE ESPAÑA": "Other",
    "UNION DEL PUEBLO NAVARRO": "Other",
    "PARTIT DEMÒCRATA EUROPEU CATALÀ-ESPAI CIU": "Other",
    "JUNTS PER CATALUNYA - JUNTS": "Other",
    "EUZKO ALDERDI JELTZALEA-PARTIDO NACIONALISTA VASCO": "Other",
    "COALICIÓN DE CENTRO DEMOCRÁTICO": "Other",
    "ALMERIENSES - REGIONALISTAS PRO ALMERÍA": "Other",
    "LIBRES": "Other",
    "CAMINANDO JUNTOS": "Other",
    "ESCAÑOS EN BLANCO PARA DEJAR ESCAÑOS VACÍOS": "Other",
    "JUNTOS POR GRANADA": "Other",
    "POR HUELVA": "Other",
    "JAÉN MERECE MÁS": "Other",
    "FEDERACIÓN DE LOS INDEPENDIENTES DE ARAGÓN": "Other",
    "ARAGÓN EXISTE - COALICIÓN EXISTE": "Other",
    "PARTIDO ARAGONÉS": "Other",
    "TERUEL EXISTE - COALICIÓN EXISTE": "Other",
    "ASTURIAS EXISTE-ESPAÑA VACIADA": "Other",
    "COALICIÓN CANARIA": "Other",
    "POR ÁVILA": "Other",
    "VÍA BURGALESA": "Other",
    "ESPAÑA VACIADA-PARTIDO CASTELLANO-TIERRA COMUNERA": "Other",
    "ESPAÑA VACIADA": "Other",
    "PARTIDO REGIONALISTA DEL PAÍS LEONÉS": "Other",
    "UNIÓN DEL PUEBLO LEONÉS": "Other",
    "VAMOS PALENCIA": "Other",
    "GRUPO INDEPENDIENTE PALENCIA TIERRA VIVA": "Other",
    "TERCERA EDAD EN ACCIÓN": "Other",
    "SORIA ¡YA!": "Other",
    "UNIDAD CASTELLANA": "Other",
    "FUERZA CÍVICA": "Other",
    "ZAMORA SÍ": "Other",
    "ESCONS EN BLANC": "Other",
    "ENTRE VEÏNS CATALUNYA": "Other",
    "UNIDOS POR LA SOLIDARIDAD INTERNACIONAL": "Other",
    "BLOQUE EXTREMEÑO": "Other",
    "SOMOS CÁCERES": "Other",
    "GEROA BAI": "Other",
    "REFERÉNDUM SISTEMA DINERO": "Other",
    "POR MI REGIÓN": "Other",
    "PARTIDO AUTÓNOMOS": "Other",
    "ESTAT VALENCIÀ DEL BENESTAR": "Other",
    "COALICIÓN POR MELILLA": "Other",
}

DICT_PARTY_IDEOLOGY_19 = {
    # VOX
    "VOX": "VOX",
    # PSOE
    "PARTIDO SOCIALISTA OBRERO ESPAÑOL": "PSOE",
    "PARTIDO SOCIALISTA DE EUSKADI-EUSKADIKO EZKERRA (PSOE)": "PSOE",
    "PARTIDO DOS SOCIALISTAS DE GALICIA-PSOE": "PSOE",
    "PARTIT DELS SOCIALISTES DE CATALUNYA": "PSOE",
    # Right-leaning
    "PARTIDO POPULAR": "Right",
    "PARTIDO POPULAR-FORO": "Right",
    "PARTIDO POPULAR / PARTIT POPULAR": "Right",
    "PARTIT POPULAR/PARTIDO POPULAR": "Right",
    "CIUDADANOS-PARTIDO DE LA CIUDADANÍA": "Right",
    "CIUTADANS-PARTIDO DE LA CIUDADANÍA": "Right",
    "NAVARRA SUMA": "Right",
    "FALANGE ESPAÑOLA DE LAS JONS": "Right",
    # Left-leaning
    "UNIDAS PODEMOS": "Left",
    "UNIDAS PODEMOS-ALTOARAGÓN EN COMÚN": "Left",
    "UNIDAS PODEMOS-XUNÍES PODEMOS": "Left",
    "UNIDAS PODEMOS-UNIDES PODEM": "Left",
    "EN COMÚ PODEM-GUANYEM EL CANVI": "Left",
    "ELKARREKIN PODEMOS-UNIDAS PODEMOS": "Left",
    "EN COMÚN-UNIDAS PODEMOS": "Left",
    "MÁS PAÍS": "Left",
    "MÁS PAÍS-CHUNTA ARAGONESISTA-EQUO": "Left",
    "MÁS PAÍS-EQUO": "Left",
    "MÁS PAÍS-CANDIDATURA ECOLOGISTA": "Left",
    "POR UN MUNDO MÁS JUSTO": "Left",
    "POR UN MUNDO MÁS JUSTO/BIDEZKO MUNDURANTZ": "Left",
    "POR UN MUNDO MÁS JUSTO/POR UN MUNDO MÁS JUSTO": "Left",
    "POR UN MUNDO MÁIS XUSTO/POR UN MUNDO MÁS JUSTO": "Left",
    "RECORTES CERO-GRUPO VERDE": "Left",
    "RECORTES CERO-GRUPO VERDE-PARTIDO CASTELLANO-TIERRA COMUNERA": "Left",
    "PARTIDO COMUNISTA DEL PUEBLO ANDALUZ": "Left",
    "PARTIDO COMUNISTA OBRERO ESPAÑOL": "Left",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA": "Left",
    "PARTIDO COMUNISTA DE LOS PUEBLOS DE ESPAÑA": "Left",
    "PARTIT COMUNISTA DEL POBLE DE CATALUNYA": "Left",
    "PARTIT COMUNISTA DELS TREBALLADORS DE CATALUNYA": "Left",
    "PARTIT COMUNISTA DELS POBLES D'ESPANYA": "Left",
    "PARTIDO COMUNISTA DEL PUEBLO CANARIO": "Left",
    "PARTIDO COMUNISTA DOS TRABALLADORES DE GALIZA": "Left",
    "PARTIDO COMUNISTA DE LOS TRABAJADORES DE EUSKADI/EUSKADIKO LANGILEEN ALDERDI KOMUNISTA": "Left",
    "PARTIDO LIBERTARIO": "Left",
    "IZQUIERDA ANTICAPITALISTA REVOLUCIONARIA": "Left",
    "IZQUIERDA EN POSITIVO": "Left",
    "INICIATIVA FEMINISTA": "Left",
    "LOS VERDES": "Left",
    "LOS VERDES ECOPACIFISTAS ADELANTE": "Left",
    "MÉS ESQUERRA": "Left",
    "MÉS COMPROMÍS": "Left",
    "PER UN MÓN MÉS JUST": "Left",
    "BIDEZKO MUNDURANTZ": "Left",
    # Other / regional / niche / protest / blank
    "ESCAÑOS EN BLANCO": "Other",
    "ESCAÑOS EN BRANCO": "Other",
    "ESCAÑOS EN BLANCO-AULKI ZURIAK": "Other",
    "ANDALUCÍA POR SÍ": "Other",
    "CONVERGENCIA ANDALUZA": "Other",
    "PARTIDO REPUBLICANO INDEPENDIENTE SOLIDARIO ANDALUZ": "Other",
    "FEDERACIÓN DE LOS INDEPENDIENTES DE ARAGÓN": "Other",
    "CHUNTA ARAGONESISTA": "Other",
    "PUYALON": "Other",
    "AUNA COMUNITAT VALENCIANA": "Other",
    "AGRUPACIÓN DE ELECTORES TERUEL EXISTE": "Other",
    "UNIÓN DE TODOS": "Other",
    "MOVIMIENTO ARAGONES SOCIAL": "Other",
    "PARTIDO HUMANISTA": "Other",
    "ANDECHA ASTUR": "Other",
    "NUEVA CANARIAS-COALICIÓN CANARIA": "Other",
    "AHORA CANARIAS: Alternativa Nacionalista Canaria (ANC) y Unidad del Pueblo": "Other",
    "PARTIDO DEMÓCRATA SOCIAL JUBILADOS EUROPEOS": "Other",
    "COALICIÓN CANARIA-NUEVA CANARIAS": "Other",
    "PARTIDO REGIONALISTA DE CANTABRIA": "Other",
    "POR ÁVILA": "Other",
    "UNIÓN DEL PUEBLO LEONÉS": "Other",
    "PARTIDO REGIONALISTA DEL PAÍS LEONÉS": "Other",
    "CENTRADOS": "Other",
    "PLATAFORMA DEL PUEBLO SORIANO": "Other",
    "UNIÓN REGIONALISTA DE CASTILLA Y LEÓN": "Other",
    "CONVERXENCIA 21": "Other",
    "EUSKAL HERRIA BILDU": "Other",
    "GEROA BAI": "Other",
    "EUZKO ALDERDI JELTZALEA-PARTIDO NACIONALISTA VASCO": "Other",
    "JUNTS PER CATALUNYA-JUNTS": "Other",
    "SOMOS REGIÓN": "Other",
    "DEMOCRACIA PLURAL": "Other",
    "AVANT ADELANTE LOS VERDES": "Other",
    "UNIDOS Actuando por la Democracia": "Other",
    "SOM VALENCIANS EN MOVIMENT": "Other",
    "MOVIMIENTO POR LA DIGNIDAD Y LA CIUDADANÍA DE CEUT": "Other",
    "COALICIÓN POR MELILLA": "Other",
    "CONTIGO SOMOS DEMOCRACIA": "Other",
}

# choose which 2023 classification scheme to use: "main_parties" or "left_right_nat"
VAR_PARTY_IDEOLOGY_SCHEME_23 = "main_parties"

DICT_PARTY_IDEOLOGY_23 = (
    DICT_PARTY_IDEOLOGY_23_MAIN_PARTIES
    if VAR_PARTY_IDEOLOGY_SCHEME_23 == "main_parties"
    else DICT_PARTY_IDEOLOGY_23_LEFT_RIGHT_NAT
)

DICT_PARTY_IDEOLOGY = (
    DICT_PARTY_IDEOLOGY_19
    if VAR_ELECTORAL_YEAR_CHOSEN == 2019
    else DICT_PARTY_IDEOLOGY_23
)
