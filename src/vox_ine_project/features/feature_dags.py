import os

import graphviz

from vox_ine_project.defaults.defaults import DIR_PLOTS

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"


def generar_dags_electorales():
    # --- DAG 1: Inmigración de América ---
    dag_soe = graphviz.Digraph(comment="DAG Inmigración América y PSOE", format="png")
    dag_soe.attr(rankdir="LR", size="10,6")

    # Definición de nodos
    dag_soe.node(
        "Renta",
        "Renta neta media de los hogares\n(Variable de Control)",
        style="filled",
        fillcolor="#e0f2fe",
    )
    dag_soe.node(
        "Inmigr",
        "Inmigración\n(pct_ext)",
        style="filled",
        fillcolor="#fef3c7",
    )
    dag_soe.node(
        "PSOE",
        "Intención de Voto al PSOE\n(Variable Objetivo)",
        style="filled",
        fillcolor="#fee2e2",
    )

    # Definición de aristas y supuestos causales
    dag_soe.edge("Renta", "Inmigr", label="(+)\nMenor concentración\nen rentas bajas")
    dag_soe.edge("Renta", "PSOE", label="(-)\nMayor apoyo al PSOE\nen rentas bajas")
    dag_soe.edge("Inmigr", "PSOE", label="(+)\nEfecto directo\npositivo")

    # Guardar y renderizar DAG 1
    dag_soe.render(DIR_PLOTS + "dag_soe.png", view=False)
    print("DAG de PSOE generado exitosamente como 'dag_soe.png'.")

    # --- DAG 2: Inmigración de África ---
    dag_vox = graphviz.Digraph(comment="DAG Inmigración África y PSOE", format="png")
    dag_vox.attr(rankdir="LR", size="10,6")

    # Definición de nodos
    dag_vox.node(
        "Renta",
        "Renta neta media de los hogares\n(Variable de Control)",
        style="filled",
        fillcolor="#e0f2fe",
    )
    dag_vox.node(
        "Inmigr",
        "Inmigración\n(pct_ext)",
        style="filled",
        fillcolor="#fef3c7",
    )
    dag_vox.node(
        "VOX",
        "Intención de Voto al PSOE\n(Variable Objetivo)",
        style="filled",
        fillcolor="#e4fee2",
    )

    # Definición de aristas y supuestos causales
    dag_vox.edge("Renta", "Inmigr", label="(-)\nMayor concentración\nen rentas bajas")
    dag_vox.edge("Renta", "VOX", label="(=)\nIgual apoyo a VOX\nen rentas bajas")
    dag_vox.edge("Inmigr", "VOX", label="(?)\nEfecto directo\ndesconocido")

    # Guardar y renderizar DAG 2
    dag_vox.render(DIR_PLOTS + "dag_vox.png", view=False)
    print("DAG de VOX generado exitosamente como 'dag_vox.png'.")


if __name__ == "__main__":
    generar_dags_electorales()
