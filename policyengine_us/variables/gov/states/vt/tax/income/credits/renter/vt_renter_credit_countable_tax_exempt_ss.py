from policyengine_us.model_api import *


class vt_renter_credit_countable_tax_exempt_ss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit countable tax exempt social security"
    unit = USD
    documentation = (
        "75 percent of the nontaxable Social Security benefits on the "
        "claimant's return, under 32 V.S.A. 6061(18)(C). A tax unit "
        "dependent's benefits are not the claimant's income."
    )
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/",  # (18)(C)
        "https://legislature.vermont.gov/statutes/section/32/154/06066",  # (b)(1)
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",  # line 11
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        # 32 V.S.A. 6066(b)(1) tests "the claimant's income", and RCC-146
        # line 11 reads the claimant's own Form 1040 lines 6a and 6b, which
        # hold the head's and spouse's benefits only.
        return (
            tax_unit("filer_tax_exempt_social_security", period)
            * p.countable_tax_exempt_ss_fraction
        )
