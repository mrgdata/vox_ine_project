import pandas as pd
import numpy as np
import os
from loguru import logger
from matplotlib import pyplot as plt
from vox_ine_project.defaults.defaults import (
    DIR_DATA,
    DIR_PLOTS,
    FILE_1,
    FILE_2,
    FILE_3,
    FILE_4,
    EXTENSION,
    SEPARATOR,
    VAR_ELECTORAL_YEAR_CHOSEN,
    DICT_HEATMAP,
)
from vox_ine_project.features.features import (
    clean_ine_data,
    merge_ine_data,
    impute_missing_data,
    create_agg_data_evolution_plot,
    create_agg_data_heatmap_plot,
    clean_election_data,
)


class GeneratePlots:
    def run(self):
        self._load_data()
        self._clean_data()
        self._create_plot_data()
        self._evolution_plot()
        self._heatmap_plot(False, n_bins=4)
        logger.success("Project have been performed completely!")

    def _load_data(self):
        """_summary_
            Ensure asset directory is available and read the data with pandas methods.

        Returns:
            tuple[pd.DataFrame]: four dataframes to be used in further methods
        """
        logger.info("Reading data...")
        if os.path.exists(DIR_DATA):
            self.df_1_ine = pd.read_csv(DIR_DATA + FILE_1 + EXTENSION, sep=SEPARATOR)
            self.df_2_ine = pd.read_csv(DIR_DATA + FILE_2 + EXTENSION, sep=SEPARATOR)
            self.df_3_ine = pd.read_csv(DIR_DATA + FILE_3 + EXTENSION, sep=SEPARATOR)
            self.df_elections = pd.read_csv(
                DIR_DATA + FILE_4 + EXTENSION, sep=SEPARATOR
            )
        else:
            logger.warning(f"{DIR_DATA} has not been found, please check your cwd")
            raise OSError("Path is not available")

        return self.df_1_ine, self.df_2_ine, self.df_3_ine, self.df_elections

    def _clean_data(self):
        logger.info("Cleaning data...")
        self.df_1_ine = clean_ine_data(self.df_1_ine)
        self.df_2_ine = clean_ine_data(self.df_2_ine)
        self.df_3_ine = clean_ine_data(self.df_3_ine)
        self.df_elections = clean_election_data(self.df_elections)

    def _create_plot_data(self):
        logger.info("Merging and creating new data...")
        self.df_ine_raw = merge_ine_data(self.df_1_ine, self.df_2_ine, self.df_3_ine)
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

    def _evolution_plot(self, show: bool = False):
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
            label="Overall Δ foreign born population",
        )

        plt.xlabel(f"Household net income {self.dist_value} (2023-based)")
        plt.ylabel("Δ foreign born population (2023 − 2021)")
        plt.title(
            f"Change in foreign born population population by household income {self.dist_value} of census sections"
        )

        plt.savefig(DIR_PLOTS + "evolution_plot.png")
        if show:
            plt.tight_layout()
            plt.show()

    def _heatmap_plot(self, show: bool = False, n_bins: int = 3):
        for var in DICT_HEATMAP.keys():
            df_agg, v_min, v_max = create_agg_data_heatmap_plot(
                self.df_heatmap, var, n_bins=n_bins
            )

            fig, ax = plt.subplots(figsize=(6, 6))

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

            ax.set_xlabel("Percentage of Immigrant Population (quantiles)")
            ax.set_ylabel("Household Net Income (quantiles)")
            ax.set_title(f"{DICT_HEATMAP[var][1]} by Income × Immigration")

            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label(DICT_HEATMAP[var][1])

            # Annotate only for small grids
            if n_bins <= 5:
                for i in range(df_agg.shape[0]):
                    for j in range(df_agg.shape[1]):
                        val = df_agg.iloc[i, j]
                        if not np.isnan(val):
                            ax.text(
                                j, i, f"{val:.1f}", ha="center", va="center", fontsize=8
                            )

            plt.tight_layout()
            plt.savefig(
                f"{DIR_PLOTS}/heatmap_{var}_{n_bins}x{n_bins}_{VAR_ELECTORAL_YEAR_CHOSEN}.png"
            )

            if show:
                plt.show()

            plt.close()
