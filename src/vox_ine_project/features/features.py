import numpy as np
import pandas as pd
import statsmodels.api as sm
from loguru import logger

from vox_ine_project.defaults.defaults import (
    DICT_DISTRIBUTION_INCOME,
    DICT_PARTY_IDEOLOGY,
    LIST_CONTINENT_TO_CHOOSE,
    LIST_LOGIT_FEATURES,
    LIST_LOGIT_INTERACTION_FEATURES,
    TUPLE_CAT_PROVINCES,
    TUPLE_PV_PROVINCES,
    VAR_CAT_BOOL,
    VAR_PV_BOOL,
)


def clean_ine_data(
    df: pd.DataFrame, cat_bool: bool = VAR_CAT_BOOL, pv_bool: bool = VAR_PV_BOOL
):
    """Clean a raw INE indicator dataframe to a consistent per-section format.

    Parameters
    ----------
    df : pd.DataFrame
        Raw INE dataframe, must contain a "Secciones" and a "Total" column.
    cat_bool : bool, optional
        If True, filter out Catalan provinces, by default VAR_CAT_BOOL.
    pv_bool : bool, optional
        If True, filter out Basque Country provinces, by default VAR_PV_BOOL.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe with a numeric "Total" column and a "key_seccion" column.
    """
    if "Distritos" not in df.columns:  # identify df_3 alternative data distribution
        df = df[df["Municipios"].notna() & df["Secciones"].notna()]
    else:
        df = df[df["Distritos"].notna() & df["Secciones"].notna()]

    mask_formacion = (
        df["Nivel de formación alcanzado"] == "Total"
        if "Nivel de formación alcanzado" in df.columns
        else pd.Series(True, index=df.index)
    )

    mask_sexo = (
        df["Sexo"] == "Total"
        if "Sexo" in df.columns
        else pd.Series(True, index=df.index)
    )

    mask_pais_nacimiento = (
        df["País de nacimiento"] != "Total"
        if "País de nacimiento" in df.columns
        else pd.Series(True, index=df.index)
    )

    df = df[mask_formacion & mask_sexo & mask_pais_nacimiento]

    df.loc[df["Total"].astype(str).str.startswith(".", "nan"), "Total"] = np.nan
    total_str = df["Total"].astype("string").str.strip()

    # Missing values and invalid leading separators
    invalid = total_str.isna() | total_str.str.startswith(r"\.", na=False)
    total_str = total_str.mask(invalid)

    # Remove thousands separators, then convert decimal commas to dots.
    # Examples: "1,00" -> "1.00", "1.000" -> "1000",
    #           "1.000,00" -> "1000.00", "1.00" -> "1.00"
    total_str = total_str.str.replace(
        r"(?<=\d)\.(?=\d{3}(?:,|$))", "", regex=True
    ).str.replace(",", ".", regex=False)

    df["Total"] = pd.to_numeric(total_str, errors="coerce").astype("float64")
    df["key_seccion"] = df["Secciones"].str[:10]

    # passed explicitly from generate_plots instead of read from defaults
    if cat_bool:
        logger.debug("filtering out catalan provinces")
        df = df[~df["key_seccion"].str.startswith(TUPLE_CAT_PROVINCES)]
    if pv_bool:
        logger.debug("filtering out basque provinces")
        df = df[~df["key_seccion"].str.startswith(TUPLE_PV_PROVINCES)]

    return df


def clean_election_data(df: pd.DataFrame):
    """Clean raw election results into one row per section with vote shares.

    Parameters
    ----------
    df : pd.DataFrame
        Raw election results, one row per party per polling station.

    Returns
    -------
    pd.DataFrame
        One row per "key_seccion", with one column per ideology holding the
        vote share percentage.
    """
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


def merge_ine_data(df1: pd.DataFrame, df2: pd.DataFrame, df4: pd.DataFrame):
    """Merge the cleaned INE dataframes and derive the analysis variables.

    Parameters
    ----------
    df1 : pd.DataFrame
        Cleaned income indicators dataframe.
    df2 : pd.DataFrame
        Cleaned demographic indicators dataframe.
    df4 : pd.DataFrame
        Cleaned disaggregated birth country indicators dataframe, containing
        both "País de nacimiento" (raw country) and "País de nacimiento_desagregado"
        (continent) columns.

    Returns
    -------
    pd.DataFrame
        Merged dataframe with "renta_neta_media_hogar", "pct_ext", "pct_america",
        "pct_africa" and "population_share" columns, one row per section/period.

    Raises
    ------
    ValueError
        If the income, demographic or birth country variables required for
        the analysis are missing after merging.
    """
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
            df4[df4["País de nacimiento_desagregado"].isin(LIST_CONTINENT_TO_CHOOSE)]
            .groupby(["key_seccion", "Periodo", "País de nacimiento_desagregado"])
            .agg({"Total": "sum"})
            .reset_index()
            .pivot(
                index=["key_seccion", "Periodo"],
                columns="País de nacimiento_desagregado",
                values="Total",
            ),
            left_index=True,
            right_index=True,
        )
        .reset_index()
    )

    # "España"/"Extranjero" totals derived from df4's raw (non-continent) "País de nacimiento" column
    pais_nacimiento = (
        df4.groupby(["key_seccion", "Periodo", "País de nacimiento"], as_index=False)
        .agg({"Total": "sum"})
        .pivot(
            index=["key_seccion", "Periodo"],
            columns="País de nacimiento",
            values="Total",
        )
    )
    pais_nacimiento["Extranjero"] = pais_nacimiento.drop(
        columns="España", errors="ignore"
    ).sum(axis=1)
    df = df.merge(
        pais_nacimiento[["España", "Extranjero"]].reset_index(),
        on=["key_seccion", "Periodo"],
        how="inner",
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
    if "América" in df.columns and "España" in df.columns:
        df["pct_america"] = round(
            100 * (df["América"] / (df["América"] + df["España"])), 2
        )
    if "África" in df.columns and "España" in df.columns:
        df["pct_africa"] = round(
            100 * (df["África"] / (df["África"] + df["España"])), 2
        )
    else:
        raise ValueError(
            "Disaggregated birth country variables for the analysis are missing, check merging process"
        )
    df["population_share"] = 100 * (df["Población"] / df["Población"].sum())

    return df


def impute_missing_data(df: pd.DataFrame):
    """Impute missing values per year using the "Municipios" group mean.

    Parameters
    ----------
    df : pd.DataFrame
        Merged INE dataframe containing a "Periodo" column with values 2021
        and 2023.

    Returns
    -------
    pd.DataFrame
        Dataframe with missing values imputed, concatenated across both years.
    """
    dfs_list = []
    for year in [2021, 2023]:
        df_year = df[df["Periodo"] == year]

        df_year = df_year[df_year["Población"].notna()]
        for col in df_year.columns:
            if df_year[col].isna().sum() > 0:
                df_year[col] = df_year[col].astype("Float64")
                municipios_average = df_year.groupby("Municipios")[col].transform(
                    "mean"
                )
                total_average = round(df_year[col].mean(), 0)
                df_year[col] = (
                    df_year[col].fillna(municipios_average).fillna(total_average)
                )
        logger.info(f"NaNs summary for {year}")
        print(df_year.isna().sum())
        dfs_list.append(df_year)

    df = pd.concat(dfs_list)

    return df


def create_agg_data_evolution_plot(
    df: pd.DataFrame, default_distribution: str = "ventile"
):
    """Aggregate the change in foreign born population by income bucket.

    Parameters
    ----------
    df : pd.DataFrame
        Merged INE dataframe containing "Periodo", "pct_ext", "Población" and
        "renta_neta_media_hogar" columns.
    default_distribution : str, optional
        Income distribution to bucket by (key of DICT_DISTRIBUTION_INCOME),
        by default "ventile".

    Returns
    -------
    tuple[pd.DataFrame, float, str]
        Aggregated migrants by income bucket, the overall delta in migrants
        and the distribution name actually used.
    """
    if default_distribution not in DICT_DISTRIBUTION_INCOME:
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

    df_23["migrants"] = (df_23["Población"] * (df_23["pct_ext"] / 100)).astype(
        "float64"
    )
    df_21["migrants"] = (df_21["Población"] * (df_21["pct_ext"] / 100)).astype(
        "float64"
    )

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


def create_agg_data_heatmap_plot(
    df: pd.DataFrame, value: str, demo_var: str = "pct_ext", n_bins: int = 3
):
    """Bin income and a demographic variable into quantiles and aggregate a value.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing "renta_neta_media_hogar", `demo_var` and `value`.
    value : str
        Column to aggregate; summed if "population_share", otherwise averaged
        weighted by "Población".
    demo_var : str, optional
        Demographic variable to bin on the second axis, by default "pct_ext".
    n_bins : int, optional
        Number of quantile bins per axis, by default 3.

    Returns
    -------
    tuple[pd.DataFrame, float, float]
        Aggregated grid (income bin x demo_var bin) and the color scale
        bounds (v_min, v_max).
    """
    df = df.copy()

    # Create quantile bins
    df["bin_a"] = pd.qcut(
        df["renta_neta_media_hogar"], q=n_bins, labels=False, duplicates="drop"
    )

    df["bin_b"] = pd.qcut(df[demo_var], q=n_bins, labels=False, duplicates="drop")

    # Aggregate
    if value == "population_share":
        agg = df.groupby(["bin_a", "bin_b"])[value].sum().unstack()
        v_min, v_max = agg.min().min(), agg.max().max()

    else:
        agg = (
            df.groupby(["bin_a", "bin_b"])
            .apply(lambda x: np.average(x[value], weights=x["Población"]))
            .unstack()
        )
        v_min = np.nanpercentile(agg.values, 10)
        v_max = np.nanpercentile(agg.values, 90)

    return agg.astype("float64"), v_min, v_max


def fit_ideology_linear_model(
    df: pd.DataFrame,
    ideology_cols: list[str],
    feature_cols: list[str] = LIST_LOGIT_FEATURES,
    interaction_features: list[str] = LIST_LOGIT_INTERACTION_FEATURES,
    weight_col: str | None = "population_share",
):
    """Fit one weighted linear regression per ideology, predicting vote share.

    Parameters
    ----------
    df : pd.DataFrame
        Data containing `feature_cols`, `interaction_features`, `ideology_cols`
        and `weight_col`.
    ideology_cols : list[str]
        Vote share columns, one per ideology; each gets its own independent
        regression.
    feature_cols : list[str], optional
        Numeric predictors for the model, by default LIST_LOGIT_FEATURES.
    interaction_features : list[str], optional
        Feature columns multiplied together into a single interaction term
        added to the model, by default LIST_LOGIT_INTERACTION_FEATURES. Pass
        an empty list to disable the interaction term.
    weight_col : str or None, optional
        Column used as the WLS observation weight, so more populous sections
        count more, by default "population_share". Pass None for plain OLS.

    Returns
    -------
    tuple[dict[str, RegressionResultsWrapper], list[str]]
        Fitted WLS/OLS result per ideology, and the ideology column names.
    """
    required_cols = list(
        dict.fromkeys(
            feature_cols
            + interaction_features
            + ideology_cols
            + ([weight_col] if weight_col else [])
        )
    )
    df = df[required_cols].dropna()

    for col in dict.fromkeys(feature_cols + interaction_features):
        df[col] = _normalize_variable(df[col])

    model_feature_cols = list(feature_cols)
    if interaction_features:
        interaction_name = ":".join(interaction_features)
        df[interaction_name] = df[interaction_features].prod(axis=1)
        model_feature_cols.append(interaction_name)

    x = sm.add_constant(df[model_feature_cols])

    results = {}
    for ideology in ideology_cols:
        y = df[ideology]
        model = sm.WLS(y, x, weights=df[weight_col]) if weight_col else sm.OLS(y, x)
        results[ideology] = model.fit()

    return results, ideology_cols


def fit_single_wls(
    df: pd.DataFrame,
    y_col: str,
    x_cols: list[str],
    weight_col: str | None = "population_share",
):
    """Ad hoc helper to fit and print a single WLS/OLS regression.

    Parameters
    ----------
    df : pd.DataFrame
        Data containing `y_col`, `x_cols` and `weight_col`.
    y_col : str
        Dependent variable column name.
    x_cols : list[str]
        Predictor column names.
    weight_col : str or None, optional
        Column used as the WLS observation weight, by default
        "population_share". Pass None for plain OLS.

    Returns
    -------
    RegressionResultsWrapper
        Fitted WLS/OLS result.
    """
    required_cols = list(dict.fromkeys(x_cols + [y_col] + ([weight_col] if weight_col else [])))
    df = df[required_cols].dropna()

    x = sm.add_constant(df[x_cols])
    y = df[y_col]

    model = sm.WLS(y, x, weights=df[weight_col]) if weight_col else sm.OLS(y, x)
    result = model.fit()

    print(result.summary())

    return result


def _normalize_variable(
    series: pd.Series,
    method: str = "zscore",
) -> pd.Series:
    """
    Normalize a numerical variable.

    Parameters
    ----------
    series : pd.Series
        Variable to normalize.
    method : str
        'zscore' : mean 0, standard deviation 1.
        'minmax' : rescales values to [0, 1].

    Returns
    -------
    pd.Series
        Normalized variable, preserving the original index.
    """
    series = series.astype("float64")

    if method == "zscore":
        std = series.std()
        if pd.isna(std) or std == 0:
            return pd.Series(0.0, index=series.index).where(series.notna())
        return (series - series.mean()) / std

    elif method == "minmax":
        min_val = series.min()
        max_val = series.max()

        if max_val == min_val or pd.isna(min_val):
            return pd.Series(0.0, index=series.index).where(series.notna())
        return (series - min_val) / (max_val - min_val)

    else:
        raise ValueError(f"Unknown method: {method!r}. Use 'zscore' or 'minmax'.")
