from policyengine_us.model_api import *


class me_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Maine TANF"
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.maine.gov/dhhs/ofi/programs-services/tanf",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762 and 10-144 C.M.R. Chapter 331
        income_eligible = spm_unit("me_tanf_income_eligible", period)
        resources_eligible = spm_unit("me_tanf_resources_eligible", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        return (
            income_eligible
            & resources_eligible
            & demographic_eligible
            & immigration_eligible
        )
