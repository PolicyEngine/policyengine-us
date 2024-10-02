from policyengine_us.model_api import *


class az_long_term_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona long-term capital gains subtraction"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=31"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.subtractions.capital_gains

        long_term_capital_gains = add(
            tax_unit, period, ["long_term_capital_gains"]
        )

        return max_(0, long_term_capital_gains) * p.rate
