from policyengine_us.model_api import *


class va_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia refundable earned income tax credit if claimed"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.va.tax.income.credits.eitc.match
        # Va. Code 58.1-339.8(B)(1) and (D) bar a dependent's return and a
        # return claiming a listed benefit; the low-income credit's poverty
        # test does not apply to the EITC alternatives.
        eligible = tax_unit("va_eitc_eligible", period)
        return eligible * p.refundable * federal_eitc
