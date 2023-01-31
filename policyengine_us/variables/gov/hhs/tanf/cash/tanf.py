from policyengine_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.hhs.tanf.abolish_tanf:
            return 0
        tanf_reported = add(spm_unit, period, ["tanf_reported"])
        if tanf_reported.sum() > 0:
            return tanf_reported
        # Obtain eligibility.
        eligible = spm_unit("is_tanf_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = spm_unit("tanf_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)
