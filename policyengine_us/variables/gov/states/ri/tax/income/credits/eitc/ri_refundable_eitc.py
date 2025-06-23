from policyengine_us.model_api import *


class ri_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island refundable earned income tax credit"
    unit = USD

    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/forms/2014/Income/2014-1040_h.pdf"  # Calculation see RI SCHEDULE EIC
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-I/44-30-2.6.htm"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        ri_eitc = tax_unit("ri_eitc", period)
        ri_income_tax_before_refundable_credits = tax_unit(
            "ri_income_tax_before_refundable_credits", period
        )
        p = parameters(period).gov.states.ri.tax.income.credits.eitc
        # refundable earned-income credit is the percent of the amount by which the Rhode Island earned-income credit exceeds the Rhode Island income tax.
        return max_(
            0,
            p.refundable
            * (
                ri_eitc
                - min_(ri_eitc, ri_income_tax_before_refundable_credits)
            ),
        )
