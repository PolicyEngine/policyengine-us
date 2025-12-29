from policyengine_us.model_api import *


class ga_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia TANF due to income"
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        # Gross income test - use federal TANF variables
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        gross_income_ceiling = spm_unit("ga_tanf_gross_income_ceiling", period)
        passes_gross_test = gross_income <= gross_income_ceiling

        # Net income test
        countable_income = spm_unit("ga_tanf_countable_income", period)
        standard_of_need = spm_unit("ga_tanf_standard_of_need", period)
        passes_net_test = countable_income < standard_of_need

        return passes_gross_test & passes_net_test
