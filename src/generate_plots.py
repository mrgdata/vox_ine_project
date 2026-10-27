import os

import numpy as np
import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt

from vox_ine_project.defaults.defaults import (
    DICT_BIN_NAME_DEFAULT,
    DICT_BIN_NAMES,
    DICT_CONTINENT,
    DICT_DEMO_VAR_LABELS,
    DICT_EVOLUTION_PLOT_LABELS,
    DICT_HEATMAP,
    DICT_HEATMAP_LABELS,
    DICT_IDEOLOGY_LOGIT_LABELS,
    DIR_DATA,
    DIR_PLOTS,
    EXTENSION,
    FILE_1,
    FILE_2,
    FILE_4,
    FILE_5,
    LIST_HEATMAP_DEMO_VARS,
    SEPARATOR,
    VAR_CAT_BOOL,
    VAR_ELECTORAL_YEAR_CHOSEN,
    VAR_LANGUAGE,
    VAR_PV_BOOL,
)
from vox_ine_project.features.features import (
    clean_election_data,
    clean_ine_data,
    create_agg_data_evolution_plot,
    create_agg_data_heatmap_plot,
    fit_ideology_logit_model,
    impute_missing_data,
    merge_ine_data,
)


class GeneratePlots:
    def run(
        self,
        n_bins: int = 4,
        language: str = VAR_LANGUAGE,
        cat_bool: bool = VAR_CAT_BOOL,
        pv_bool: bool = VAR_PV_BOOL,
    ):
        """Run the full pipeline: load, clean and merge data, then plot everything.

        Parameters
        ----------
        n_bins : int, optional
            Number of quantile bins used for the heatmaps, by default 4.
        language : str, optional
            Language used for plot labels ("en" or "es"), by default VAR_LANGUAGE.
        cat_bool : bool, optional
            If True, filter out Catalan provinces, by default VAR_CAT_BOOL.
        pv_bool : bool, optional
            If True, filter out Basque Country provinces, by default VAR_PV_BOOL.
        """
        self._load_data()
        self._clean_data(cat_bool=cat_bool, pv_bool=pv_bool)
        self._create_plot_data()
        self._evolution_plot(language=language)
        self._heatmap_plot(False, n_bins=n_bins, language=language)
        self._ideology_logit_plot(False, language=language)
        logger.success("Project have been performed completely!")

    def _load_data(self):
        """Read the raw INE and election data files into instance attributes.

        Raises
        ------
        OSError
            If the data directory does not exist.
        """
        logger.info("Reading data...")
        if os.path.exists(DIR_DATA):
            self.df_1_ine = pd.read_csv(DIR_DATA + FILE_1 + EXTENSION, sep=SEPARATOR)
            self.df_2_ine = pd.read_csv(DIR_DATA + FILE_2 + EXTENSION, sep=SEPARATOR)
            self.df_4_ine = pd.read_csv(DIR_DATA + FILE_4 + EXTENSION, sep=SEPARATOR)
            self.df_elections = pd.read_csv(
                DIR_DATA + FILE_5 + EXTENSION, sep=SEPARATOR
            )
        else:
            logger.warning(f"{DIR_DATA} has not been found, please check your cwd")
            raise OSError("Path is not available")

    def _clean_data(self, cat_bool: bool = VAR_CAT_BOOL, pv_bool: bool = VAR_PV_BOOL):
        """Clean the raw INE and election dataframes loaded by `_load_data`.

        Parameters
        ----------
        cat_bool : bool, optional
            If True, filter out Catalan provinces, by default VAR_CAT_BOOL.
        pv_bool : bool, optional
            If True, filter out Basque Country provinces, by default VAR_PV_BOOL.
        """
        logger.info("Cleaning data...")
        self.df_1_ine = clean_ine_data(
            self.df_1_ine, cat_bool=cat_bool, pv_bool=pv_bool
        )
        self.df_2_ine = clean_ine_data(
            self.df_2_ine, cat_bool=cat_bool, pv_bool=pv_bool
        )
        self.df_4_ine = clean_ine_data(
            self.df_4_ine, cat_bool=cat_bool, pv_bool=pv_bool
        )
        self.df_4_ine["País de nacimiento_desagregado"] = (
            self.df_4_ine["País de nacimiento"]
            .map(DICT_CONTINENT)
            .fillna(self.df_4_ine["País de nacimiento"])
        )
        self.df_elections = clean_election_data(self.df_elections)

    def _create_plot_data(self):
        """Merge the cleaned dataframes, impute missing values and build plot inputs."""
        logger.info("Merging and creating new data...")
        self.df_ine_raw = merge_ine_data(
            self.df_1_ine, self.df_2_ine, self.df_4_ine
        )
        self.df_ine = impute_missing_data(self.df_ine_raw)
        self.df_heatmap = self.df_elections.merge(
            self.df_ine[self.df_ine["Periodo"] == VAR_ELECTORAL_YEAR_CHOSEN].copy(),
            on="key_seccion",
            how="inner",
        )
        (
            self.df_agg_evolution_plot,
            self.overall_delta_evolution_plot,
            self.dist_value,
        ) = create_agg_data_evolution_plot(self.df_ine)

    def _evolution_plot(self, show: bool = False, language: str = VAR_LANGUAGE):
        """Plot the change in foreign born population by household income bucket.

        Parameters
        ----------
        show : bool, optional
            If True, display the plot interactively, by default False.
        language : str, optional
            Language used for plot labels ("en" or "es"), by default VAR_LANGUAGE.
        """
        if language not in DICT_EVOLUTION_PLOT_LABELS:
            logger.warning(
                f"Language '{language}' is not supported, defaulting to 'en'"
            )
            language = "en"
        text = DICT_EVOLUTION_PLOT_LABELS[language]

        logger.info("Creating and saving plots...")
        plt.figure(figsize=(9, 5))

        plt.bar(
            self.df_agg_evolution_plot[f"income_{self.dist_value}"],
            self.df_agg_evolution_plot["delta_migrants"],
            color="gray",
        )
        plt.axhline(
            self.overall_delta_evolution_plot,
            linestyle="--",
            linewidth=1,
            color="black",
            label=text["legend_label"],
        )

        plt.xlabel(text["xlabel"].format(dist_value=self.dist_value))
        plt.ylabel(text["ylabel"])
        plt.title(text["title"].format(dist_value=self.dist_value))

        plt.savefig(DIR_PLOTS + "evolution_plot.png")
        if show:
            plt.tight_layout()
            plt.show()

    def _heatmap_plot(
        self, show: bool = False, n_bins: int = 3, language: str = VAR_LANGUAGE
    ):
        """Plot and save one heatmap per demographic variable x ideology variable.

        One heatmap is generated for every combination of demographic variable
        in `LIST_HEATMAP_DEMO_VARS` (e.g. "pct_ext", "pct_america", "pct_africa")
        and ideology/population variable in `DICT_HEATMAP`, binning household
        income against the demographic variable.

        Parameters
        ----------
        show : bool, optional
            If True, display each plot interactively, by default False.
        n_bins : int, optional
            Number of quantile bins per axis, by default 3.
        language : str, optional
            Language used for plot labels ("en" or "es"), by default VAR_LANGUAGE.
        """
        if language not in DICT_HEATMAP_LABELS:
            logger.warning(
                f"Language '{language}' is not supported, defaulting to 'en'"
            )
            language = "en"
        text = DICT_HEATMAP_LABELS[language]
        bin_name = DICT_BIN_NAMES.get(n_bins, DICT_BIN_NAME_DEFAULT)[language]

        for demo_var in LIST_HEATMAP_DEMO_VARS:
            if demo_var not in self.df_heatmap.columns:
                continue
            demo_label = DICT_DEMO_VAR_LABELS[demo_var][language]

            for var in DICT_HEATMAP:
                if var not in self.df_heatmap.columns:
                    continue
                var_label = DICT_HEATMAP[var][1][language]
                df_agg, v_min, v_max = create_agg_data_heatmap_plot(
                    self.df_heatmap, var, demo_var=demo_var, n_bins=n_bins
                )

                _, ax = plt.subplots(figsize=(6, 6))

                im = ax.imshow(
                    df_agg.values,
                    origin="lower",
                    cmap=DICT_HEATMAP[var][0],
                    vmin=v_min,
                    vmax=v_max,
                    aspect="auto",
                )

                # Axis ticks
                ticks = np.arange(n_bins)
                labels = [f"Q{i + 1}" for i in range(n_bins)]

                ax.set_xticks(ticks)
                ax.set_yticks(ticks)
                ax.set_xticklabels(labels)
                ax.set_yticklabels(labels)

                ax.set_xlabel(
                    text["xlabel"].format(bin_name=bin_name, demo_label=demo_label)
                )
                ax.set_ylabel(text["ylabel"].format(bin_name=bin_name))
                ax.set_title(
                    text["title"].format(var_label=var_label, demo_label=demo_label)
                )

                # Colorbar
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label(text["cbar_label"].format(var_label=var_label))

                # Annotate only for small grids
                if n_bins <= 5:
                    for i in range(df_agg.shape[0]):
                        for j in range(df_agg.shape[1]):
                            val = df_agg.iloc[i, j]
                            if not np.isnan(val):
                                ax.text(
                                    j,
                                    i,
                                    f"{val:.1f}",
                                    ha="center",
                                    va="center",
                                    fontsize=8,
                                )

                plt.tight_layout()
                plt.savefig(
                    f"{DIR_PLOTS}/heatmap_{var}_{demo_var}_{n_bins}x{n_bins}_{VAR_ELECTORAL_YEAR_CHOSEN}.png"
                )

                if show:
                    plt.show()

                plt.close()

    def _ideology_logit_plot(self, show: bool = False, language: str = VAR_LANGUAGE):
        """Fit a multinomial logit model of each section's dominant ideology and plot it.

        The model predicts the ideology with the highest vote share in each
        census section from "pct_ext", "pct_america", "pct_africa" and
        "renta_neta_media_hogar". The fitted summary is logged and the
        resulting coefficients are plotted relative to the base category.

        Parameters
        ----------
        show : bool, optional
            If True, display the plot interactively, by default False.
        language : str, optional
            Language used for plot labels ("en" or "es"), by default VAR_LANGUAGE.
        """
        if language not in DICT_IDEOLOGY_LOGIT_LABELS:
            logger.warning(
                f"Language '{language}' is not supported, defaulting to 'en'"
            )
            language = "en"
        text = DICT_IDEOLOGY_LOGIT_LABELS[language]

        logger.info("Fitting multinomial logit model for dominant ideology...")
        ideology_cols = [
            var
            for var in DICT_HEATMAP
            if var != "population_share" and var in self.df_heatmap.columns
        ]

        result, categories = fit_ideology_logit_model(self.df_heatmap, ideology_cols)
        # statsmodels' MNLogit drops the last (highest-coded) category as base, not the first
        base_category = categories[-1]
        logger.info(f"Base (reference) category: {base_category}")
        logger.info("\n" + str(result.summary()))

        params = result.params.copy()
        params.columns = [categories[int(col)] for col in params.columns]
        params = params.drop(index="const", errors="ignore")

        _, ax = plt.subplots(figsize=(8, 6))
        params.plot(kind="bar", ax=ax)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xlabel(text["xlabel"])
        ax.set_ylabel(text["ylabel"])
        ax.set_title(text["title"].format(base_category=base_category))
        ax.legend(
            title=text["legend_title"], bbox_to_anchor=(1.02, 1), loc="upper left"
        )
        plt.tight_layout()
        plt.savefig(
            f"{DIR_PLOTS}/ideology_logit_coefficients_{VAR_ELECTORAL_YEAR_CHOSEN}.png"
        )

        if show:
            plt.show()

        plt.close()
