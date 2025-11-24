from policyengine_us.model_api import *


class mo_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-05/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Missouri TANF counts most unearned income sources
        # SSI and Section 8 housing are excluded
        income_sources = [
            "social_security",
            "unemployment_compensation",
            "alimony_income",
            "child_support_received",
            "veterans_benefits",
        ]

        return add(spm_unit, period, income_sources)
