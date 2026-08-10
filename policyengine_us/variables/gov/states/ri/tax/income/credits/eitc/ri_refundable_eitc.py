from policyengine_us.model_api import *


class ri_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island refundable earned income tax credit"
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-I/44-30-2.6.htm"
    )

    def formula(tax_unit, period, parameters):
        ri_eitc = tax_unit("ri_eitc", period)
        tax_before_refundable_credits = tax_unit(
            "ri_income_tax_before_refundable_credits", period
        )
        p = parameters(period).gov.states.ri.tax.income.credits.eitc
        # The portion of the RI EITC up to the tax liability offsets tax
        # dollar-for-dollar; only refundable_percent of the excess over the
        # liability is refunded (100% from 2015, 15% before 2015).
        non_refundable_portion = min_(ri_eitc, tax_before_refundable_credits)
        excess_over_liability = ri_eitc - non_refundable_portion
        return non_refundable_portion + p.refundable_percent * excess_over_liability
