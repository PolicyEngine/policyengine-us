from policyengine_us.model_api import *


class mn_renters_credit_household_agi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota renter's credit household adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        person_agi = person("adjusted_gross_income_person", period)
        is_dependent = person("is_tax_unit_dependent", period) | person(
            "claimed_as_dependent_on_another_return", period
        )
        tax_unit_person_agi = person.tax_unit.sum(person_agi)
        tax_unit_agi = person.tax_unit("adjusted_gross_income", period)
        is_head = person("is_tax_unit_head", period)
        tax_unit_agi_fallback = (
            (tax_unit_person_agi == 0) * is_head * ~is_dependent * tax_unit_agi
        )
        return spm_unit.sum(person_agi * ~is_dependent + tax_unit_agi_fallback)
