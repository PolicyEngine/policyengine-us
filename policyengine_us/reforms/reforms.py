from .congress.delauro import create_american_family_act_with_baby_bonus_reform
from .winship import create_eitc_winship_reform
from policyengine_core.reforms import Reform
import warnings


def create_structural_reforms_from_parameters(parameters, period):
    afa_reform = create_american_family_act_with_baby_bonus_reform(
        parameters, period
    )
    winship_reform = create_eitc_winship_reform(parameters, period)

    if afa_reform is not None:
        if winship_reform is not None:
            warnings.warn(
                "Both the American Family Act and the Winship EITC reform are enabled. Multiple structural reforms are not yet supported, so only the American Family Act will be applied."
            )
        return afa_reform
    elif winship_reform is not None:
        return winship_reform
