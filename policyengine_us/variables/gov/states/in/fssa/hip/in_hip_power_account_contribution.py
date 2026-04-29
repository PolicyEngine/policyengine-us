from policyengine_us.model_api import *


class in_hip_power_account_contribution(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana HIP POWER Account annual contribution"
    unit = USD
    documentation = (
        "Annual Indiana Healthy Indiana Plan (HIP) POWER Account contribution "
        "paid by the tax unit. Monthly per-adult tier keyed on the tax unit's "
        "income as a fraction of the federal poverty line, multiplied by the "
        "count of HIP-eligible adults and by twelve months. Returns zero when "
        "the collection flag is false (true value since 2020-03-01 per the "
        "COVID-19 public health emergency and continued suspension after the "
        "2024 court ruling)."
    )
    definition_period = YEAR
    defined_for = StateCode.IN
    reference = "https://www.in.gov/fssa/hip/about-hip/power-accounts/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.hip.power_account
        if not p.active:
            return 0
        n_hip_adults = tax_unit.sum(tax_unit.members("is_hip_eligible_adult", period))
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        monthly_per_adult = p.contribution_amount.calc(income_level)
        return monthly_per_adult * n_hip_adults * MONTHS_IN_YEAR
