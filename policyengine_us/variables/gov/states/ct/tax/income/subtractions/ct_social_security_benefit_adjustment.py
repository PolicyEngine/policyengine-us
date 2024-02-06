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
        # Line 41, Part A and Part B
        us_taxable_ss = tax_unit("tax_unit_taxable_social_security", period)
        ss_portion = us_taxable_ss * p.rate.social_security
        combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )
        # Line 41, Part C and Part D
        # Lesser of 25% of combined income excess and 25% of taxable social security benefits
        capped_ss_portion = min_(
            ss_portion, p.combined_income_excess * combined_income_excess
        )

        agi = tax_unit("adjusted_gross_income", period)
        # Line 41, Part E and Part F
        # Difference between taxable social security benefits and capped social security portion
        adjusted_ss_benefit = max_(us_taxable_ss - capped_ss_portion, 0)
        reduction_threshold = p.reduction_threshold[filing_status]
        # Adjustment determined based on AGI amount compared to reduction threshold
        return where(
            agi < reduction_threshold, us_taxable_ss, adjusted_ss_benefit
        )
