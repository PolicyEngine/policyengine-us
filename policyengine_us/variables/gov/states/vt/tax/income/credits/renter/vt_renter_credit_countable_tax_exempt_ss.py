from policyengine_us.model_api import *


class vt_renter_credit_countable_tax_exempt_ss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit countable tax exempt social security"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/",  # (18)(C)
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        # Section 6061(18)(C) counts "Social Security benefits as defined
        # under 26 U.S.C. § 86(d)", and 86(d)(1)(B) includes tier 1 railroad
        # benefits.
        excluded_benefits = add(
            tax_unit,
            period,
            [
                "tax_exempt_social_security",
                "tax_exempt_railroad_social_security_equivalent_benefits",
            ],
        )
        return excluded_benefits * p.countable_tax_exempt_ss_fraction
