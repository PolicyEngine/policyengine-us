from policyengine_us.model_api import *


class de_529_plan_subtraction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware subtraction for contributions to 529 plans on a joint return"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The subtraction on a single-column return. Spouses filing a joint "
        "return subtract their combined contributions up to the joint limit, "
        "tested on their joint federal adjusted gross income. For an unmarried "
        "filer this equals de_529_plan_subtraction."
    )
    reference = (
        # 30 Del. C. § 1106(b)(11)
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
        # 2023 PIT-RES instructions, line 8b
        "https://revenuefiles.delaware.gov/2023/PIT-RES_TY23_2023-01_Instructions.pdf#page=7",
        # 2024 PIT-RES instructions, line 8b ("married filing separately combined ...
        # whose individual federal adjusted gross income")
        "https://revenuefiles.delaware.gov/2024/PIT_2024_Forms/PIT_Instructions/PIT-RES_TY24_2024-01_Instructions.pdf#page=7",
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions.plan_529
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        contributions = tax_unit.sum(
            person("investment_in_529_plan_indv", period) * head_or_spouse
        )
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        eligible = agi <= p.agi_limit[filing_status]
        return eligible * min_(contributions, p.cap[filing_status])
