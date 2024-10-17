from policyengine_us.model_api import *


class ri_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island refundable earned income tax credit"
    unit = USD
    documentation = (
        "44-30-2.6. Rhode Island taxable income — Rate of tax. (N)(2)"
    )
    definition_period = YEAR
    reference = "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-I/44-30-2.6.htm"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        ri_eitc = tax_unit("ri_eitc", period)
        ri_income_tax_before_refundable_credits = tax_unit("ri_income_tax_before_refundable_credits", period)
        p = parameters(period).gov.states.ri.tax.income.credits.eitc

        return max(0, p.refundable * (ri_eitc - min(ri_eitc, ri_income_tax_before_refundable_credits)))
