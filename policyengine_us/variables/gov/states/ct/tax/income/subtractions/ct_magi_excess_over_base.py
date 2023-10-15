from policyengine_us.model_api import *


class ct_magi_excess_over_base(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut excess of modified adjusted gross income and social security over base amount"
    definition_period = YEAR
    defined_for = StateCode.CT

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
