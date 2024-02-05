from policyengine_us.model_api import *


class vt_renter_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6066/"  # b
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36"
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        # line 10
        irs_gross_income = add(tax_unit, period, ["irs_gross_income"])
        # line 11
        total_social_security = tax_unit("tax_unit_social_security", period)
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        non_taxable_ss_cap = max(
            0, total_social_security - taxable_social_security
        )
        non_taxable_social_security = (
            non_taxable_ss_cap * p.rate.non_taxable_ss
        )
        # line 12
        tax_emempt_interest_income = add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )
        #  line 13  we do not include loss add-bacls in the calculation
        # add line 10 through 12
        return (
            irs_gross_income
            + non_taxable_social_security
            + tax_emempt_interest_income
        )
