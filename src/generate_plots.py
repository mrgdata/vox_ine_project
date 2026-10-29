import os

import numpy as np
import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Patch

from vox_ine_project.defaults.defaults import (
    DICT_BIN_NAME_DEFAULT,
    DICT_BIN_NAMES,
    DICT_CONTINENT,
    DICT_DEMO_VAR_LABELS,
    DICT_EVOLUTION_PLOT_LABELS,
    DICT_HEATMAP,
    DICT_HEATMAP_LABELS,
    DICT_IDEOLOGY_COEF_LABELS,
    DIR_DATA,
    DIR_PLOTS,
    EXTENSION,
    FILE_1,
    FILE_2,
    FILE_4,
    FILE_5,
    LIST_HEATMAP_DEMO_VARS,
    LIST_LOGIT_FEATURES,
    LIST_LOGIT_INTERACTION_FEATURES,
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
    fit_ideology_linear_model,
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
        self._ideology_linear_plot(False, language=language)
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
        self.df_ine_raw = merge_ine_data(self.df_1_ine, self.df_2_ine, self.df_4_ine)
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

        # neutral color, intensity scaled by each bucket's population_share
        pop_share = self.df_agg_evolution_plot["population_share"]
        norm = Normalize(vmin=pop_share.min(), vmax=pop_share.max())
        bar_colors = plt.get_cmap("Greys")(norm(pop_share))

        plt.bar(
            self.df_agg_evolution_plot[f"income_{self.dist_value}"],
            self.df_agg_evolution_plot["delta_migrants"],
            color=bar_colors,
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

    def _ideology_linear_plot(self, show: bool = False, language: str = VAR_LANGUAGE):
        """Fit a weighted linear regression of each ideology's vote share and plot it.

        One regression is fit per ideology, predicting its vote share from
        `LIST_LOGIT_FEATURES`, weighted by "population_share". If
        "renta_neta_media_hogar" is one of those features, the models and
        plots are additionally produced without it, to check its role as a
        confounder between immigration and vote share.

        Parameters
        ----------
        show : bool, optional
            If True, display the plot interactively, by default False.
        language : str, optional
            Language used for plot labels ("en" or "es"), by default VAR_LANGUAGE.
        """
        if language not in DICT_IDEOLOGY_COEF_LABELS:
            logger.warning(
                f"Language '{language}' is not supported, defaulting to 'en'"
            )
            language = "en"
        text = DICT_IDEOLOGY_COEF_LABELS[language]

        logger.info("Fitting linear regression models for ideology vote shares...")
        ideology_cols = [
            var
            for var in DICT_HEATMAP
            if var != "population_share" and var in self.df_heatmap.columns
        ]

        if "renta_neta_media_hogar" in LIST_LOGIT_FEATURES:
            logger.info(
                "'renta_neta_media_hogar' is a model feature; fitting models with "
                "and without it to check its role as a confounder between "
                "immigration and vote share"
            )
            features_without_income = [
                f for f in LIST_LOGIT_FEATURES if f != "renta_neta_media_hogar"
            ]
            interaction_without_income = [
                f
                for f in LIST_LOGIT_INTERACTION_FEATURES
                if f != "renta_neta_media_hogar"
            ]
            if len(interaction_without_income) < 2:
                interaction_without_income = []

            self._fit_and_plot_ideology_model(
                ideology_cols,
                LIST_LOGIT_FEATURES,
                LIST_LOGIT_INTERACTION_FEATURES,
                "with_income",
                show,
                text,
            )
            self._fit_and_plot_ideology_model(
                ideology_cols,
                features_without_income,
                interaction_without_income,
                "without_income",
                show,
                text,
            )
        else:
            self._fit_and_plot_ideology_model(
                ideology_cols,
                LIST_LOGIT_FEATURES,
                LIST_LOGIT_INTERACTION_FEATURES,
                None,
                show,
                text,
            )

    def _fit_and_plot_ideology_model(
        self,
        ideology_cols: list[str],
        feature_cols: list[str],
        interaction_features: list[str],
        suffix: str | None,
        show: bool,
        text: dict,
    ):
        """Fit one WLS model per ideology for the given features and plot its coefficients.

        Parameters
        ----------
        ideology_cols : list[str]
            Vote share columns, one per ideology.
        feature_cols : list[str]
            Numeric predictors passed to `fit_ideology_linear_model`.
        interaction_features : list[str]
            Feature columns multiplied together into an interaction term.
        suffix : str or None
            Appended to the plot title and saved filename to distinguish model
            variants (e.g. "with_income"/"without_income").
        show : bool
            If True, display the plot interactively.
        text : dict
            Plot label strings for the chosen language.
        """
        results, ideology_cols = fit_ideology_linear_model(
            self.df_heatmap,
            ideology_cols,
            feature_cols=feature_cols,
            interaction_features=interaction_features,
        )
        for ideology, result in results.items():
            logger.info(
                f"\n{ideology} ({suffix or 'default'})\n" + str(result.summary())
            )

        params = pd.DataFrame(
            {ideology: result.params for ideology, result in results.items()}
        ).drop(index="const", errors="ignore")
        pvalues = pd.DataFrame(
            {ideology: result.pvalues for ideology, result in results.items()}
        ).drop(index="const", errors="ignore")

        # solid color per ideology, sampled from its DICT_HEATMAP colormap
        category_colors = {
            ideology: plt.get_cmap(DICT_HEATMAP[ideology][0])(0.65)
            for ideology in params.columns
        }

        _, ax = plt.subplots(figsize=(8, 6))
        params.plot(
            kind="bar", ax=ax, color=[category_colors[c] for c in params.columns]
        )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xlabel(text["xlabel"])
        ax.set_ylabel(text["ylabel"])
        ax.set_title(
            text["title"] + (f" ({suffix.replace('_', ' ')})" if suffix else "")
        )

        legend_handles = [
            Patch(facecolor=category_colors[ideology], label=ideology)
            for ideology in params.columns
        ]

        significance_level = 0.05
        for container, ideology in zip(ax.containers, params.columns):
            for patch, predictor in zip(container, params.index):
                if pvalues.loc[predictor, ideology] >= significance_level:
                    patch.set_alpha(0.35)

        ax.legend(
            handles=legend_handles,
            title=text["legend_title"],
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
        )
        plt.tight_layout()
        filename_suffix = f"_{suffix}" if suffix else ""
        plt.savefig(
            f"{DIR_PLOTS}/ideology_vote_share_coefficients_{VAR_ELECTORAL_YEAR_CHOSEN}{filename_suffix}.png"
        )

        if show:
            plt.show()

        plt.close()
