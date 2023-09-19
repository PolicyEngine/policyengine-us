from policyengine_us.model_api import *


class az_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Military Retirement Subtraction"
    unit = USD
    reference = (
        "https://www.azleg.gov/ars/43/01022.html",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=25",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=27",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        military_retirement_pay = person("military_retirement_pay", period)
        eligible_military_pay = military_retirement_pay * head_or_spouse
        capped_military_pay = min_(eligible_military_pay, p.military_retirement_subtraction)
        return tax_unit.sum(capped_military_pay)
           