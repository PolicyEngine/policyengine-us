from policyengine_us.model_api import *


class tanf(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "TANF"
    documentation = (
        "Value of Temporary Assistance for Needy Families benefit received, "
        "summing all state-specific TANF programs."
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.hhs.tanf
        if p.abolish_tanf:
            return 0

        # Use reported TANF if available
        tanf_reported = add(spm_unit, period, ["tanf_reported"])
        if tanf_reported.sum() > 0:
            return tanf_reported

        # Sum all state TANF programs
        # Each state has its own implementation in the states/ folder
        STATES_WITH_TANF = ["ca", "co", "dc", "ny"]
        return add(
            spm_unit, period, [f"{state}_tanf" for state in STATES_WITH_TANF]
        )
