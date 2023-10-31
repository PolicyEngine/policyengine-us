from policyengine_us.model_api import *


class az_military_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona military pension subtraction"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=15"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.subtractions.military_pension
        person = tax_unit.members

        military_retirement_pay = min_(
            p.cap, person("military_retirement_pay", period)
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return tax_unit.sum(military_retirement_pay * (head_or_spouse))
