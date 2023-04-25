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
        # First compute TANF for states with it defined in gov/hhs/tanf.
        # This is IL and CA.
        # (We will move these into gov/states)
        # Obtain eligibility.
        eligible = spm_unit("is_tanf_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = spm_unit("tanf_amount_if_eligible", period)
        # Add TANF programs computed in variables/gov/states.
        STATES_WITH_TANF = ["co", "ny", "dc"]
        state_tanf = add(
            spm_unit, period, [i + "_tanf" for i in STATES_WITH_TANF]
        )
        return where(eligible, amount_if_eligible, 0) + state_tanf
