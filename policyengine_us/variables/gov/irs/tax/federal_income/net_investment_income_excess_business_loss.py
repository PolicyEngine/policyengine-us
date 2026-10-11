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
        "rental and Form 4835 farm rental losses, and the parts of estate and "
        "trust and partnership/S corporation losses that net investment "
        "income includes. Section 1411(c)(1)(B) allows only the deductions "
        "allowed by chapter 1, so net investment income adds this back. When "
        "the head and spouse also have business losses net investment income "
        "does not count, the excess is shared in proportion to the two kinds "
        "of loss; no statute, regulation or form instruction says how to "
        "split it."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#c_1_B",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.ecfr.gov/current/title-26/section-1.1411-4#p-1.1411-4(f)",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        rental_loss = max_(0, -person("rental_income", period))
        farm_rent_loss = max_(0, -person("farm_rent_income", period))
        # Only the part of each section 461(l) loss that net investment
        # income also counts: the estate and trust loss after the Schedule
        # K-1 (Form 1041) code H adjustment, and the passive part of the
        # partnership/S corporation loss.
        estate_loss = min_(
            max_(0, -person("estate_net_investment_income", period)),
            max_(0, -person("estate_income", period)),
        )
        passive_loss = min_(
            max_(0, -person("passive_partnership_s_corp_income", period)),
            max_(0, -person("partnership_s_corp_income", period)),
        )
        investment_loss = tax_unit.sum(
            not_dependent * (rental_loss + farm_rent_loss + estate_loss + passive_loss)
        )
        _, business_loss = section_461l_business_income_and_loss(tax_unit, period)
        investment_share = np.divide(
            investment_loss,
            business_loss,
            out=np.zeros_like(investment_loss),
            where=business_loss > 0,
        )
        return tax_unit("excess_business_loss", period) * investment_share
