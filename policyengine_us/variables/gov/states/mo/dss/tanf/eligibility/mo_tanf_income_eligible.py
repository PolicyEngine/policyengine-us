from policyengine_us.model_api import *


class mo_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF income eligibility (passes all three income tests)"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Must pass all three income tests sequentially
        passes_185_test = spm_unit("mo_tanf_185_percent_test", period)
        passes_standard_of_need_test = spm_unit(
            "mo_tanf_standard_of_need_test", period
        )
        passes_percentage_of_need_test = spm_unit(
            "mo_tanf_percentage_of_need_test", period
        )

        return (
            passes_185_test
            & passes_standard_of_need_test
            & passes_percentage_of_need_test
        )
