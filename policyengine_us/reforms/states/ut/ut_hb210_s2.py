from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ut_hb210_s2() -> Reform:
    """
    Utah HB 210 Substitute 2 - Marriage tax credit (Section 59-10-1049)

    Creates a standalone nonrefundable marriage tax credit:
    - $158 for joint and surviving spouse filers
    - $79 for married filing separately
    - MAGI income limits: $90,000 (joint/surviving), $45,000 (separate)
    - Hard cutoff, no phaseout

    This is separate from the taxpayer credit add-on in the original bill
    and Substitute 1 (implemented in ut_hb210.py).
    """

    def modify_parameters(parameters):
        # Add ut_hb210_s2_marriage_credit to non-refundable credits list
        non_refundable = (
            parameters.gov.states.ut.tax.income.credits.non_refundable
        )
        current_credits = non_refundable(instant("2026-01-01"))
        if "ut_hb210_s2_marriage_credit" not in current_credits:
            new_credits = list(current_credits) + [
                "ut_hb210_s2_marriage_credit"
            ]
            non_refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=new_credits,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_ut_hb210_s2_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_hb210_s2()

    p = parameters.gov.contrib.states.ut.hb210.s2_marriage_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_hb210_s2()
    else:
        return None


ut_hb210_s2 = create_ut_hb210_s2_reform(None, None, bypass=True)
