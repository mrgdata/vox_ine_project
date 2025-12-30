import pandas as pd
from loguru import logger
import numpy as np
from vox_ine_project.defaults.defaults import (
    VAR_CAT_BOOL,
    TUPLE_CAT_PROVINCES,
    TUPLE_PV_PROVINCES,
    VAR_PV_BOOL,
    DICT_DISTRIBUTION_INCOME,
    DICT_PARTY_IDEOLOGY,
)


def clean_ine_data(df: pd.DataFrame):
    """_summary_

    Args:
        df (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """
    if "Distritos" not in df.columns:  # identify df_3 alternative data distribution
        df = df[df["Municipios"].notna() & df["Secciones"].notna()]
        df = df[
            (df["Nivel de formación alcanzado"] == "Total")
            & (df["País de nacimiento"] != "Total")
        ]
    else:
        df = df[df["Distritos"].notna() & df["Secciones"].notna()]

    df.loc[df["Total"].astype(str).str.startswith(".", "nan"), "Total"] = np.nan
    df["Total"] = (
        df["Total"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["key_seccion"] = df["Secciones"].str[:10]

    if VAR_CAT_BOOL:
        logger.debug("filtering out catalan provinces")
        df = df[~df["key_seccion"].str.startswith(TUPLE_CAT_PROVINCES)]
    if VAR_PV_BOOL:
        logger.debug("filtering out basque provinces")
        df = df[~df["key_seccion"].str.startswith(TUPLE_PV_PROVINCES)]

    return df


def clean_election_data(df: pd.DataFrame):
    df["key_seccion"] = (
        df["codigo_provincia"].astype(str).str.zfill(2)
        + df["codigo_municipio"].astype(str).str.zfill(3)
        + df["codigo_distrito"].astype(str).str.zfill(2)
        + df["codigo_seccion"].astype(str).str.zfill(3)
    )

    df["ideology"] = df["denominacion"].map(DICT_PARTY_IDEOLOGY).fillna("Other")
    df = df.groupby(["key_seccion", "ideology"], as_index=False).agg(
        votos=("votos", "sum")
    )

    # vote share within each municipio
    df["vote_share"] = round(
        (df["votos"] / df.groupby("key_seccion")["votos"].transform("sum")) * 100,
        2,
    )

    # one column per ideology
    df = (
        df.pivot(index="key_seccion", columns="ideology", values="vote_share").fillna(0)
    ).reset_index()

    return df


def merge_ine_data(df1: pd.DataFrame, df2: pd.DataFrame, df3: pd.DataFrame):
    df = (
        df1.pivot(
            index=[
                "Municipios",
                "key_seccion",
                "Periodo",
            ],  # add here Municipios since it will be useful afterwards
            columns="Indicadores de renta media",
            values="Total",
        )
        .merge(
            df2.pivot(
                index=["key_seccion", "Periodo"],
                columns="Indicadores demográficos",
                values="Total",
            ),
            left_index=True,
            right_index=True,
        )
        .merge(
            df3.pivot(
                index=["key_seccion", "Periodo"],
                columns="País de nacimiento",
                values="Total",
            ),
            left_index=True,
            right_index=True,
        )
        .reset_index()
    )

    # check basic columns to assure merging is done correctly
    if "Renta neta media por hogar" in df.columns:
        df.rename(
            columns={"Renta neta media por hogar": "renta_neta_media_hogar"},
            inplace=True,
        )
    else:
        raise ValueError(
            "Income variables for the analysis are missing, check merging process"
        )
    if "Extranjero" in df.columns and "España" in df.columns:
        df["pct_ext"] = round(
            100 * (df["Extranjero"] / (df["Extranjero"] + df["España"])), 2
        )
    else:
        raise ValueError(
            "Demgraphic variables for the analysis are missing, check merging process"
        )
    df["population_share"] = 100 * (df["Población"] / df["Población"].sum())

    return df


def impute_missing_data(df: pd.DataFrame):
    dfs_list = []
    for year in [2021, 2023]:
        df_year = df[df["Periodo"] == year]

        df_year = df_year[df_year["Población"].notna()]
        for col in df_year.columns:
            if df_year[col].isna().sum() > 0:
                df_year[col] = (
                    df_year[col]
                    .fillna(df_year.groupby("Municipios")[col].transform("mean"))
                    .fillna(round(df_year[col].mean(), 0))
                )
        logger.info(f"NaNs summary for {year}")
        print(df_year.isna().sum())
        dfs_list.append(df_year)

    df = pd.concat(dfs_list)

    return df


def create_agg_data_evolution_plot(
    df: pd.DataFrame, default_distribution: str = "ventile"
):
    if default_distribution not in DICT_DISTRIBUTION_INCOME.keys():
        logger.warning(
            "chosen distribution is not available, change defaults or 'ventile' will be chosen"
        )
        default_distribution = "ventile"
    logger.info(
        f"default distribution for the evolution plot is {default_distribution}"
    )
    default_dist_value = DICT_DISTRIBUTION_INCOME[default_distribution]

    df_23 = df[df["Periodo"] == 2023].copy()
    df_21 = df[df["Periodo"] == 2021].copy()

    df_23["migrants"] = df_23["Población"] * (df_23["pct_ext"] / 100)
    df_21["migrants"] = df_21["Población"] * (df_21["pct_ext"] / 100)

    df_23[f"income_{default_distribution}"] = pd.qcut(
        df_23["renta_neta_media_hogar"], q=default_dist_value, labels=False
    )

    income_map = df_23[["key_seccion", f"income_{default_distribution}"]]
    df_21 = df_21.merge(income_map, on="key_seccion", how="inner")

    agg_23 = (
        df_23.groupby(f"income_{default_distribution}")["migrants"]
        .sum()
        .rename("migrants_2023")
    )

    agg_21 = (
        df_21.groupby(f"income_{default_distribution}")["migrants"]
        .sum()
        .rename("migrants_2021")
    )

    agg = pd.concat([agg_21, agg_23], axis=1).reset_index()

    agg["delta_migrants"] = 100 * (
        (agg["migrants_2023"] - agg["migrants_2021"]) / agg["migrants_2021"]
    )

    overall_delta: float = 100 * (
        (df_23["migrants"].sum() - df_21["migrants"].sum()) / df_21["migrants"].sum()
    )

    return agg, overall_delta, default_distribution


def create_agg_data_heatmap_plot(df: pd.DataFrame, value: str):
    # 1. Compute percentiles for col_a and col_b
    quantiles_a = df["renta_neta_media_hogar"].quantile([0.25, 0.75]).values
    quantiles_b = df["pct_ext"].quantile([0.25, 0.75]).values

    # 2. Define a function to assign bins
    def assign_bin(value, q25, q75):
        if value <= q25:
            return 0  # bottom 25%
        elif value <= q75:
            return 1  # middle 50%
        else:
            return 2  # top 25%

    df["bin_a"] = df["renta_neta_media_hogar"].apply(
        assign_bin, q25=quantiles_a[0], q75=quantiles_a[1]
    )
    df["bin_b"] = df["pct_ext"].apply(
        assign_bin, q25=quantiles_b[0], q75=quantiles_b[1]
    )

    # 3. Aggregate: sum of votes per bin
    if value == "population_share":
        agg = (
            df.groupby(["bin_a", "bin_b"]).apply(lambda x: np.sum(x[value])).unstack()
        )  # rows=bin_a, cols=bin_b
        v_min: float = 5.00
        v_max: float = 20.00
    else:
        agg = (
            df.groupby(["bin_a", "bin_b"])
            .apply(lambda x: np.average(x[value], weights=x["Población"]))
            .unstack()
        )  # rows=bin_a, cols=bin_b
        v_min: float = np.quantile(df[value], 0.25)
        v_max: float = np.quantile(df[value], 0.75)
    return agg, v_min, v_max
