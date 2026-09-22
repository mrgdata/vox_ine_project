import argparse

from vox_ine_project.defaults import defaults


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate VOX/INE plots")
    parser.add_argument(
        "--year",
        type=int,
        choices=[2019, 2023],
        default=defaults.VAR_ELECTORAL_YEAR_CHOSEN,
        help="Electoral year to analyze",
    )
    parser.add_argument(
        "--language",
        choices=list(defaults.DICT_HEATMAP_LABELS.keys()),
        default=defaults.VAR_LANGUAGE,
        help="Language used for heatmap titles and axis labels",
    )
    parser.add_argument(
        "--n-bins",
        type=int,
        default=4,
        help="Number of bins used for the heatmap quantile grid",
    )
    parser.add_argument(
        "--party-scheme",
        choices=["main_parties", "left_right_nat"],
        default=defaults.VAR_PARTY_IDEOLOGY_SCHEME_23,
        help="2023 party ideology classification scheme",
    )
    return parser.parse_args()


def apply_overrides(args: argparse.Namespace) -> None:
    # these constants are derived at import time, so they must be recomputed
    # here before generate_plots (and features) get imported for the first time
    defaults.VAR_ELECTORAL_YEAR_CHOSEN = args.year
    defaults.VAR_PARTY_IDEOLOGY_SCHEME_23 = args.party_scheme
    defaults.FILE_4 = "congreso19" if args.year == 2019 else "congreso23"
    defaults.DICT_PARTY_IDEOLOGY_23 = (
        defaults.DICT_PARTY_IDEOLOGY_23_MAIN_PARTIES
        if args.party_scheme == "main_parties"
        else defaults.DICT_PARTY_IDEOLOGY_23_LEFT_RIGHT_NAT
    )
    defaults.DICT_PARTY_IDEOLOGY = (
        defaults.DICT_PARTY_IDEOLOGY_19
        if args.year == 2019
        else defaults.DICT_PARTY_IDEOLOGY_23
    )


if __name__ == "__main__":
    args = parse_args()
    apply_overrides(args)

    from generate_plots import GeneratePlots

    project_execution = GeneratePlots()
    project_execution.run(n_bins=args.n_bins, language=args.language)
