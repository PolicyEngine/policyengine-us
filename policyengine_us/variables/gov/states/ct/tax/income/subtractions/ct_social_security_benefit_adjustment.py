from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    reference = (
        # Connecticut General Statutes, Chapter 229, Sec. 12-701, (20), (b), (x), (iii) and (iv)
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701"
        # 2022 Form CT-1040 Connecticut Resident Income Tax Return Instructions
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=24"
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security
        filing_status = tax_unit("filing_status", period)

        ss_rate = p.rate
        # Line 41, Part A and Part B
        total_ss = add(tax_unit, period, ["social_security"])
        ss_fraction = total_ss * ss_rate
        excess = tax_unit("ct_magi_excess_over_base", period)
        # Line 41, Part C and Part D
        max_inclusion = min_(ss_fraction, ss_rate * excess)

        agi = tax_unit("adjusted_gross_income", period)
        # Line 41, Part E and Part F
        adjusted_ss_benefit = max_(total_ss - max_inclusion, 0)
        income_limit = p.income_limit[filing_status]
        return where(agi < income_limit, total_ss, adjusted_ss_benefit)
