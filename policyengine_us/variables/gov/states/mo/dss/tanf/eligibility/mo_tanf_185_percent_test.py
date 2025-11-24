from policyengine_us.model_api import *


class mo_tanf_185_percent_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF 185% gross income test eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-05-185/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf
        standard_of_need = spm_unit("mo_tanf_standard_of_need", period)
        income_for_test = spm_unit("mo_tanf_income_for_185_test", period)

        # Income must be less than 185% of Standard of Need
        income_limit = (
            standard_of_need * p.income_limit.gross_income_percentage
        )

        return income_for_test < income_limit
