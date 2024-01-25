from policyengine_us.model_api import *


class az_public_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Pension Exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=18"
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=23"
        "https://www.azleg.gov/ars/43/01022.htm"
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.subtractions.pension
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        pension_income = person("taxable_public_pension_income", period)
        eligible_pension_income = pension_income * head_or_spouse
        total_allowed_pension_exclusion = min_(
            p.public_pension_cap, eligible_pension_income
        )
        return tax_unit.sum(total_allowed_pension_exclusion)
