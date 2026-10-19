from policyengine_us.model_api import *


class state_payroll_premium_deduction_share(Variable):
    value_type = float
    entity = Person
    label = "State payroll premium deduction share"
    documentation = (
        "Share of the permitted employee premium deducted from wages, for "
        "state programs whose premium the statute puts on the employer and "
        "lets it deduct up to a share from wages. It is "
        "employer_state_payroll_premium_deduction_share held between 0 and 1: "
        "an employer may not deduct more than the permitted share, and "
        "deducting less than nothing has no meaning."
    )
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        share = person("employer_state_payroll_premium_deduction_share", period)
        return clip(share, 0, 1)
