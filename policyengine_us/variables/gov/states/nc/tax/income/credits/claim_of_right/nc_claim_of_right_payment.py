from policyengine_us.model_api import *


class nc_claim_of_right_payment(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina tax payment for restored claim of right income"
    unit = USD
    documentation = (
        "A filer whose federal tax is computed under 26 U.S.C. 1341(a)(5) is "
        "considered to have paid North Carolina tax equal to the increase in "
        "the earlier year's North Carolina tax from including the restored "
        "income, minus the decrease in this year's North Carolina tax because "
        "the item was deductible. An overpayment it creates is refunded."
    )
    definition_period = YEAR
    reference = (
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-266.2.html",
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/HTML/1997-1998/SL1997-213.html",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        person = tax_unit.members
        increase = person("nc_claim_of_right_prior_year_tax_increase", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_increase = tax_unit.sum(increase * head_or_spouse)
        # Term (ii), the decrease in this year's North Carolina tax because
        # the item was deductible, is zero: under section 1341(a)(5) the
        # repayment is not deducted federally (section 1341(b)(3)), and
        # G.S. 105-153.5(a)(2)d allows no North Carolina deduction for it.
        return where(credit_applies, prior_year_tax_increase, 0)
