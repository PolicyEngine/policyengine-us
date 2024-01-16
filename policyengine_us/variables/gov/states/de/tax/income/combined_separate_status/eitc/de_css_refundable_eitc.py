from policyengine_us.model_api import *


class de_css_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware individual refundable earned income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2021/TY21_PIT-RSS_2021-01_PaperInteractive.pdf#page=1"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        """
        In the case of spouses who file a joint federal return, but who elect to file separate or
        combined separate returns for Delaware, the credit may only be applied against the tax
        imposed on the spouse with the higher taxable income reported on Line 22
        """
        p = parameters(period).gov.states.de.tax.income.credits.eitc
        # How to Get the higher tax_after_non_refundable_credits between head and spouse
        tax_after_non_refundable_credit = tax_unit(
            "de_income_tax_before_non_refundable_credits", period
        ) - tax_unit("de_non_refundable_credits", period)

        federal_eitc = tax_unit("eitc", period)
        refundable_eitc_cal = federal_eitc * p.refundable
        refundabele_eitc_eligibility = (
            refundable_eitc_cal >= tax_after_non_refundable_credit
        )
        return where(refundabele_eitc_eligibility, refundable_eitc_cal, 0)
