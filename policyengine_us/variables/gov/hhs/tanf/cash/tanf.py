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
    defined_for = "is_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.tanf
        if p.abolish_tanf:
            return 0
        tanf_reported = add(spm_unit, period, ["tanf_reported"])
        if tanf_reported.sum() > 0:
            return tanf_reported

        # Federal TANF calculation for eligible families
        federal_tanf = spm_unit("tanf_amount_if_eligible", period)

        # State TANF programs
        STATES_WITH_TANF = ["co", "ny", "dc"]
        state_tanf = add(
            spm_unit, period, [i + "_tanf" for i in STATES_WITH_TANF]
        )
        return federal_tanf + state_tanf
