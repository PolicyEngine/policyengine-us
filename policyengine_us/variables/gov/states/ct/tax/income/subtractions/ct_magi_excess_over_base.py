from policyengine_us.model_api import *


class ct_magi_excess_over_base(Variable):
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
        ss = parameters(period).gov.irs.social_security.taxability
        gross_ss = tax_unit("tax_unit_social_security", period)

        ss_fraction = ss.rate.lower * gross_ss
        modified_agi_plus_half_ss = (
            tax_unit("taxable_ss_magi", period) + ss_fraction
        )
        filing_status = tax_unit("filing_status", period)

        base_amount = ss.threshold.lower[filing_status]

        return max_(0, modified_agi_plus_half_ss - base_amount)
