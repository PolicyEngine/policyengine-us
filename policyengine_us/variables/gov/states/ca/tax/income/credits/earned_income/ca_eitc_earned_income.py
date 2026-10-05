from policyengine_us.model_api import *


class ca_eitc_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "California earned income for the CalEITC and YCTC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2023/2023-3514-instructions.html",  # Lines 13-19, Worksheet 3
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # FTB 3514 line 19 adds wages (line 16), nontaxable combat pay (line 17)
        # and business income or (loss) (line 18, Worksheet 3: Schedule 1
        # business and farm income less the deductible part of SE tax) for the
        # whole return. A self-employment loss therefore offsets wages,
        # including the other spouse's, before the result is floored at zero.
        person = tax_unit.members
        p = parameters(period).gov.irs.ald.misc
        se_tax_adjustment = (
            (1 - p.self_emp_tax_adj)
            * p.employer_share
            * person("self_employment_tax", period)
        )
        net_earnings = person("earned_income", period) - se_tax_adjustment
        is_dependent = person("is_tax_unit_dependent", period)
        return max_(0, tax_unit.sum(net_earnings * ~is_dependent))
