from policyengine_us.model_api import *


def create_personal_credit() -> Reform:

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("standard_deduction")
            self.neutralize_variable("eitc")
            self.neutralize_variable("ctc")

    return reform


def create_personal_credit_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_personal_credit()

    p = parameters(period).gov.contrib.personal_credit

    if p.in_effect:
        return create_personal_credit()
    else:
        return None


personal_credit = create_personal_credit_reform(None, None, bypass=True)
