from policyengine_us.model_api import *


class ms_ccpp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Mississippi CCPP monthly family co-payment"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=39"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.copay
        p_income = parameters(period).gov.states.ms.dhs.ccpp.income

        # Floor income at zero so negative self-employment income cannot inflate
        # or reduce the co-payment.
        monthly_income = max_(spm_unit("ms_ccpp_countable_income", period), 0)

        # Family size is capped at the published "6 or more" row.
        size = spm_unit("spm_unit_size", period.this_year)
        fee_scale_size = min_(size, p.max_family_size)

        # Select the co-payment rate band by position relative to 50% SMI.
        monthly_smi = spm_unit("hhs_smi", period.this_year) / MONTHS_IN_YEAR
        very_low_income = (
            monthly_income <= monthly_smi * p_income.very_low_income_smi_rate
        )
        copay_rate = where(
            very_low_income,
            p.rate.very_low_income.calc(fee_scale_size),
            p.rate.low_income.calc(fee_scale_size),
        )
        scale_copay = monthly_income * copay_rate

        # Families at or below the federal poverty line, TANF recipients, and
        # homeless families with no countable income pay no co-payment.
        monthly_fpg = spm_unit("spm_unit_fpg", period.this_year) / MONTHS_IN_YEAR
        at_or_below_fpl = monthly_income <= monthly_fpg * p.fpg_exempt_rate
        is_tanf = spm_unit("is_tanf_enrolled", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        homeless_no_income = is_homeless & (monthly_income == 0)
        zero_copay = at_or_below_fpl | is_tanf | homeless_no_income

        # Minimum-fee categories (income above the poverty line) cap the
        # co-payment at $10/month. Of the manual's categories, only protective
        # services, SSI-disabled parents, and special-needs children can be
        # tracked at the moment.
        person = spm_unit.members
        has_protective_child = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_ssi_disabled = person("is_ssi_disabled", period.this_year)
        has_ssi_disabled_parent = spm_unit.any(is_head_or_spouse & is_ssi_disabled)
        has_special_needs_child = spm_unit.any(person("is_disabled", period.this_year))
        in_min_fee_category = (
            has_protective_child | has_ssi_disabled_parent | has_special_needs_child
        )
        capped_copay = where(
            in_min_fee_category,
            min_(scale_copay, p.minimum_fee_categories_cap),
            scale_copay,
        )

        return where(zero_copay, 0, capped_copay)
