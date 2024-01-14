from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment_magi_excess(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Excess of modified adjusted gross income and social security over base amount calculation for the Connecticut social security subtraction"
    reference = (
        # Connecticut General Statutes, Chapter 229, Sec. 12-701, (20), (b), (x), (iii) and (iv)
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701"
        # Section 86(b)(1) of the Internal Revenue Code
        "https://www.law.cornell.edu/uscode/text/26/86"
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    # Code extracted from tax_unit_taxable_social_security
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)
        # Modified adjusted gross income plus 50% of social security benefits
        ss_fraction = p.rate.lower * gross_ss
        modified_agi_plus_half_ss = (
            tax_unit("taxable_ss_magi", period) + ss_fraction
        )
        # Base amount for social security threshold based on filing status
        filing_status = tax_unit("filing_status", period)
        base_amount = p.threshold.lower[filing_status]
        # Difference between MAGI calculation and base amount
        return max_(0, modified_agi_plus_half_ss - base_amount)
