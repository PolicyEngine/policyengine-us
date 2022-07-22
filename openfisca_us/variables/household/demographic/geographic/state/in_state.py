from openfisca_us.model_api import *


def create_in_state_variable(state: str) -> Type[Variable]:
    return type(
        state,
        (Variable,),
        {
            "definition_period": YEAR,
            "label": f"In {state}",
            "value_type": bool,
            "entity": Household,
            "formula": in_state(state),
        },
    )


def create_50_state_variables() -> List[Type[Variable]]:
    return [create_in_state_variable(state) for state in STATES]
