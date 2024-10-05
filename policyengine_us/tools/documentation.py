from IPython.display import Markdown, display_markdown
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

from policyengine_core.enums import Enum
from policyengine_core.charts import (
    LIGHTER_BLUE,
    LIGHT_BLUE,
    BLUE,
    DARK_BLUE,
    format_fig,
    display_fig,
)
from policyengine_us.system import system
from policyengine_us import Simulation


def variable_summary(variable_name: str):
    variable = system.variables.get(variable_name)
    metadata_df = pd.DataFrame(
        {
            "Name": [variable.name],
            "Label": [variable.label],
            "Entity": [variable.entity.key],
            "Definition period": [variable.definition_period],
            "Has a formula": [variable.formula is not None],
            "Value type": [variable.value_type.__name__],
            "Unit": [variable.unit],
            "Documentation": [variable.documentation],
            "Reference": [variable.reference],
            "Quantity type": [variable.quantity_type],
        }
    )

    if variable.defined_for is not None:
        metadata_df["Defined for"] = [f"`{variable.defined_for}`"]
    else:
        metadata_df["Defined for"] = ["All entities"]

    if variable.value_type == Enum:
        metadata_df["Possible values"] = [variable.possible_values.__name__]
        metadata_df["Default value"] = [variable.default_value]

    metadata_df = metadata_df.T.rename(columns={0: "Value"})
    metadata_df.index.name = "Metadata"
    metadata_df = metadata_df.fillna("None")

    return metadata_df


def variation_chart(
    variable: str,
    axis: str = "employment_income",
    y_axis_min: float = 0,
    y_axis_max: float = None,
    state: str = "CA",
    in_notebook: bool = False,
    additional_adult_data: dict = None,
    additional_child_data: dict = None,
    child_count_list: list = [0, 1, 2, 3],
):
    dfs = []

    if additional_adult_data is None:
        additional_adult_data = {}

    if additional_child_data is None:
        additional_child_data = {}

    adult_template = dict(
        age=30,
        **additional_adult_data,
    )

    child_template = dict(
        age=10,
        **additional_child_data,
    )

    for adults in [1, 2]:
        for children in child_count_list:
            people = dict()
            for i in range(adults):
                people[f"adult_{i}"] = adult_template
            for i in range(children):
                people[f"child_{i}"] = child_template
            situation = dict(
                people=people,
                household=dict(
                    state_code=state,
                ),
                axes=[[dict(name=axis, min=0, max=100_000, count=101)]],
            )
            sim = Simulation(situation=situation)
            earnings = sim.calculate(axis, map_to="spm_unit")
            values = sim.calculate(variable, map_to="spm_unit")
            dfs += [
                pd.DataFrame(
                    {
                        "Adults": adults,
                        "Children": children,
                        system.variables[axis].label: earnings,
                        system.variables[variable].label: values,
                    }
                )
            ]

    df = pd.concat(dfs)

    fig = px.line(
        df,
        x=system.variables[axis].label,
        y=system.variables[variable].label,
        color="Children",
        facet_col="Adults",
        facet_col_spacing=0.1,
        color_discrete_sequence=[LIGHTER_BLUE, LIGHT_BLUE, BLUE, DARK_BLUE],
    )
    fig.update_xaxes(
        tickformat="$,.0f",
    )
    max_data_value = max(df[system.variables[variable].label])
    # Round up to nearest value in same order of magnitude
    max_data_value = 10 ** (len(str(int(max_data_value))) - 1) * (
        1 + int(max_data_value / 10 ** (len(str(int(max_data_value))) - 1))
    )
    fig.update_yaxes(
        tickformat="$,.0f",
        range=(y_axis_min, y_axis_max or max_data_value),
    )

    fig.layout.annotations[0].text = "Single"
    fig.layout.annotations[1].text = "Couple"

    if in_notebook:
        return format_fig(fig)
    return display_fig(format_fig(fig))
