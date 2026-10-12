from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.limited_business_loss import (
    section_461l_business_income_and_loss,
)


class net_investment_income_excess_business_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Excess business loss attributed to net investment income"
    unit = USD
    documentation = (
        "The part of the head and spouse's section 461(l) excess business "
        "loss that falls on losses net investment income counts: Schedule E "
        "rental, Form 4835 farm rental and Schedule E Part III estate and "
        "trust losses, and the passive part of partnership/S corporation "
        "losses. Section 1411(c)(1)(B) allows only the deductions allowed by "
        "chapter 1, so net investment income adds this back. A Schedule K-1 "
        "(Form 1041) box 14 code H adjustment is a separate Form 8960 line 7 "
        "item and does not change how much of an estate or trust loss is a "
        "net investment income loss. When the head and spouse also have "
        "business losses net investment income does not count, the excess is "
        "provisionally shared in proportion to the two kinds of loss: no "
        "statute, regulation or form instruction says how to split it."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#c_1_B",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.ecfr.gov/current/title-26/section-1.1411-4#p-1.1411-4(f)",
        # Beneficiary reporting: code H is positive only for section 1291 fund,
        # CFC and QEF distributions that are NII but not taxable income.
        "https://www.irs.gov/pub/irs-prior/i1041--2025.pdf#page=38",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        rental_loss = max_(0, -person("rental_income", period))
        farm_rent_loss = max_(0, -person("farm_rent_income", period))
        estate_loss = max_(0, -person("estate_income", period))
        # Only the passive part of a partnership/S corporation loss is a net
        # investment income loss, and no more than the loss section 461(l)
        # counts.
        passive_loss = min_(
            max_(0, -person("passive_partnership_s_corp_income", period)),
            max_(0, -person("partnership_s_corp_income", period)),
        )
        investment_loss = tax_unit.sum(
            not_dependent * (rental_loss + farm_rent_loss + estate_loss + passive_loss)
        )
        _, business_loss = section_461l_business_income_and_loss(tax_unit, period)
        # Provisional proportional split; see the documentation.
        investment_share = np.divide(
            investment_loss,
            business_loss,
            out=np.zeros_like(investment_loss),
            where=business_loss > 0,
        )
        return tax_unit("excess_business_loss", period) * investment_share
