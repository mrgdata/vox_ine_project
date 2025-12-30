# Income Segregation, Immigrant Population and Electoral Choice Dynamics (Spain)

This project studies cross-sectional spanish census data in 2021 and 2023 about immigrant population, household income and national elections, with the objective of analyze the opportunities and risks of current parties in all Spain neighbourhoods.

An initial result of this project can be read in [Medium](https://medium.com/@mromgar99/el-futuro-de-vox-est%C3%A1-en-getafe-no-en-el-barrio-salamanca-07ccadac14f2).

---

## Data

The working datasets are thought to be available in assets/data and come from the [Spanish National Institute of Statistics (INE)](https://www.ine.es/dyngs/Prensa/ADRH2023.htm) and from the [Spanish Goverment Electoral Data official page](https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/), retrieved in Dec. 2025. References about files can be read in defaults.

The datasets regarding electoral data have been cleaned up based on the original .DAT files with the help of an [unofficial open source R package available in GitHub](https://github.com/rOpenSpain/infoelectoral), to be adapted to Python in a near future by the owner of this project. The retrieval of data is as simple as running the following code (working in an R version 4.5.2):

```r
devtools::install_github("ropenspain/infoelectoral")
library(infoelectoral)
df19 <- mesas(tipo_eleccion = "congreso", anno = 2019, mes = "11")
df23 <- mesas(tipo_eleccion = "congreso", anno = 2023, mes = "07")
write.table(
    df19,
    file = "congreso19.csv",
    sep = ";",
    row.names = FALSE,
    col.names = TRUE,
    quote = FALSE
)
write.table(
    df23,
    file = "congreso23.csv",
    sep = ";",
    row.names = FALSE,
    col.names = TRUE,
    quote = FALSE
)
```

## Methodology (Summary)

1. **Missing data**
Variables have been imputed by the mean by district or by the mean of the "municipio" in each year, and, if neither were available, the mean of all data have been used. The imputation affects roughly between 1 and 5% of total data, so the bias is minimal.

2. **Filters**
Data regarding Catalonia and Basque Country have been filtered out regarding the relevance of nationalist parties and the cultural and economic difference between them and the rest of Spain, requiring a separate analysis. However, it is possible to run the main script including them and the results still hold.

3. **Party classification**
The party classification is open to interpretation, but national-wide parties have been classified in left or right, separating only VOX and PSOE, since their comparison was the objetive of the first project. Other parties outside these classification have been labeled together.


## Project structure

```vox_ine_project/
├── README.md
├── pyproject.toml
├── .gitignore
├── assets/
│   └── data/
│   └── plots/
├── src/
│   └── vox_ine_project/
│       ├── __init__.py
│       ├── features
│       │    ├── clean_data.py
│       ├── defaults
│       │    └── defaults.py
│       ├── main.py
│       └── generate_plots.py
├── tests/
│   ├── __init__.py
│   └── test.py -TBD-
└── requirements.txt
```


## Notes

This repository is intended for **research and exploratory analysis**, not for
production deployment. Reproducibility is prioritized over performance.
