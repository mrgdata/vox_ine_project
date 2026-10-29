import os

import graphviz

from vox_ine_project.defaults.defaults import DIR_PLOTS

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"


def generar_dags_electorales():
    # --- DAG 1: Inmigración de América ---
    dag_am = graphviz.Digraph(comment="DAG Inmigración América y PSOE", format="png")
    dag_am.attr(rankdir="LR", size="10,6")

    # Definición de nodos
    dag_am.node(
        "Renta",
        "Renta Neta Media del Hogar\n(Variable de Control)",
        style="filled",
        fillcolor="#e0f2fe",
    )
    dag_am.node(
        "America",
        "Inmigración América\n(pct_america)",
        style="filled",
        fillcolor="#d1fae5",
    )
    dag_am.node(
        "PSOE",
        "Intención de Voto al PSOE\n(Variable Objetivo)",
        style="filled",
        fillcolor="#fee2e2",
    )

    # Definición de aristas y supuestos causales
    dag_am.edge("Renta", "America", label="(+)\nMenor concentración\nen rentas bajas")
    dag_am.edge("Renta", "PSOE", label="(-)\nMayor apoyo al PSOE\nen rentas bajas")
    dag_am.edge("America", "PSOE", label="(+)\nEfecto directo\npositivo")

    # Guardar y renderizar DAG 1
    dag_am.render(DIR_PLOTS + "dag_america_psoe.png", view=False)
    print("DAG de América generado exitosamente como 'dag_america_psoe.png'.")

    # --- DAG 2: Inmigración de África ---
    dag_af = graphviz.Digraph(comment="DAG Inmigración África y PSOE", format="png")
    dag_af.attr(rankdir="LR", size="10,6")

    # Definición de nodos
    dag_af.node(
        "Renta",
        "Renta Neta Media del Hogar\n(Variable de Control)",
        style="filled",
        fillcolor="#e0f2fe",
    )
    dag_af.node(
        "Africa",
        "Inmigración África\n(pct_africa)",
        style="filled",
        fillcolor="#fef3c7",
    )
    dag_af.node(
        "PSOE",
        "Intención de Voto al PSOE\n(Variable Objetivo)",
        style="filled",
        fillcolor="#fee2e2",
    )

    # Definición de aristas y supuestos causales
    dag_af.edge("Renta", "Africa", label="(-)\nMayor concentración\nen rentas bajas")
    dag_af.edge("Renta", "PSOE", label="(-)\nMayor apoyo al PSOE\nen rentas bajas")
    dag_af.edge("Africa", "PSOE", label="(-)\nEfecto directo\nnegativo")

    # Guardar y renderizar DAG 2
    dag_af.render(DIR_PLOTS + "dag_africa_psoe.png", view=False)
    print("DAG de África generado exitosamente como 'dag_africa_psoe.png'.")


if __name__ == "__main__":
    generar_dags_electorales()
