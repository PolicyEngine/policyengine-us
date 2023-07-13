from .congress.delauro import create_american_family_act_with_baby_bonus_reform
from .winship import create_eitc_winship_reform


def create_structural_reforms_from_parameters(parameters, period):
    afa_reform = create_american_family_act_with_baby_bonus_reform(
        parameters, period
    )
    winship_reform = create_eitc_winship_reform(parameters, period)

    return afa_reform, winship_reform
