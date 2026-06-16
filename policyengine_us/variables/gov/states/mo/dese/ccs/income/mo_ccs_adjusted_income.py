from policyengine_us.model_api import *


class mo_ccs_adjusted_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Child Care Subsidy adjusted gross income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-050",
        "https://web.archive.org/web/20211208073807id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/045/10",
    )

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit("mo_ccs_countable_income", period)
        # Medical insurance premiums are the only deduction from monthly gross
        # income (5 CSR 25-200.050(2); Manual 2010.045.15).
        premiums = add(spm_unit, period, ["health_insurance_premiums"])
        return max_(countable_income - premiums, 0)
