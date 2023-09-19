from policyengine_us.model_api import *


class az_net_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona net capital gains subtraction"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=31"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deductions.net_capital_gains

        long_term_capital_gains = add(
            tax_unit, period, ["long_term_capital_gains"]
        )
        # net capital gain derived from investment in a qualified small business should also be subtracted

        return long_term_capital_gains * p.rate
