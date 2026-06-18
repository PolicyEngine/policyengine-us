from policyengine_us.model_api import *


class mo_ccs_adjusted_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Child Care Subsidy adjusted gross income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MO
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050"

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("mo_ccs_countable_income", period)
        # Medical insurance premiums are the only deduction from monthly gross
        # income (5 CSR 25-200.050(2); Manual sec. 5.7 Deductions from Gross
        # Income).
        premiums = add(spm_unit, period, ["health_insurance_premiums"])
        return max_(countable_income - premiums, 0)
