from policyengine_us.model_api import *


class ny_allowable_college_tuition_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York allowable college tuition expenses for the credit and deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (t)(2)(A)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.college_tuition
        person = tax_unit.members
        # Tax Law 606(t)(2)(D): an individual claimed as a dependent by
        # another taxpayer cannot claim their own tuition ("only the person
        # who claims the student as a dependent", IT-272), and a return on
        # which a filer can be claimed has no dependents (IRC 152(b)(1)).
        claimed = person("claimed_as_dependent_on_another_return", period)
        dependent = person("is_tax_unit_dependent", period)
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        allowed = ~claimed & ~(dependent & dependent_filer)
        capped = min_(person("qualified_tuition_expenses", period), p.cap)
        return tax_unit.sum(capped * allowed)
