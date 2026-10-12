from policyengine_us.model_api import *


class de_529_plan_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Delaware subtraction for contributions to 529 plans on each filer's column"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The subtraction each filer takes in their own column: an unmarried "
        "filer's return, or each spouse's column when spouses file separate or "
        "combined separate returns. A joint return uses "
        "de_529_plan_subtraction_joint instead."
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

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions.plan_529
        # A dependent's contributions belong on the dependent's own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        contributions = person("investment_in_529_plan_indv", period) * head_or_spouse
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # Each spouse in a separate or combined separate column is held to the
        # individual limits and tested on the federal adjusted gross income in
        # their own column. An unmarried filer's column is the whole return.
        cap = where(joint, p.cap.SEPARATE, p.cap[filing_status])
        agi_limit = where(joint, p.agi_limit.SEPARATE, p.agi_limit[filing_status])
        agi = where(
            joint,
            person("adjusted_gross_income_person", period),
            person.tax_unit("adjusted_gross_income", period),
        )
        # No subtraction for a filer whose federal AGI is greater than the limit.
        eligible = agi <= agi_limit
        return eligible * min_(contributions, cap)
