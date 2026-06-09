from policyengine_us.model_api import *


class la_ccap_daily_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP daily co-payment"
    unit = USD
    reference = "https://www.louisianabelieves.com/docs/default-source/early-childhood/ccap-sliding-fee-scale.pdf"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap
        # Categorically eligible households pay no co-payment because the
        # state pays 100% of the maximum rate (LAC 28:CLXV.515.B); the sliding
        # fee scale also waives co-payments for families experiencing
        # homelessness. Early Head Start-Child Care Partnership enrollment is
        # not tracked at the moment.
        categorical = spm_unit("la_ccap_categorically_eligible", period)
        homeless = spm_unit.household("is_homeless", period.this_year)
        income = max_(spm_unit("la_ccap_countable_income", period), 0)
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, p.household_size.minimum, p.household_size.maximum)
        tops = p.copay.band_top
        band = (
            (income > tops.zero_copay[capped_size]).astype(int)
            + (income > tops.two_dollar[capped_size]).astype(int)
            + (income > tops.three_dollar[capped_size]).astype(int)
            + (income > tops.eight_dollar[capped_size]).astype(int)
        )
        scale_copay = p.copay.daily_amount.calc(band)
        return where(categorical | homeless, 0, scale_copay)
