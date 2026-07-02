from policyengine_us.model_api import *


class va_529_plan_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia 529 plan deduction allocated to each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        # The 529 deduction is a household contribution, not a person's income,
        # so prorate it by federal AGI share. When the household has no positive
        # federal AGI, assign it to the head so the per-person amounts still sum
        # to the household deduction.
        total = person.tax_unit("va_529_plan_deduction", period)
        person_fagi = person("adjusted_gross_income_person", period)
        total_federal_agi = person.tax_unit.sum(person_fagi)
        share = where(
            total_federal_agi > 0,
            person_fagi / total_federal_agi,
            person("is_tax_unit_head", period),
        )
        return total * share
