from policyengine_us.model_api import *


class ks_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Kansas Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-70",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-50",
        "https://ksrevisor.gov/statutes/chapters/ch39/039_007_0009.html",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        gross_income_eligible = spm_unit(
            "ks_tanf_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("ks_tanf_income_eligible", period)
        resources_eligible = spm_unit("ks_tanf_resources_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & gross_income_eligible
            & net_income_eligible
            & resources_eligible
        )
