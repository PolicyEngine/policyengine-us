from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mo.dese.ccs.mo_ccs_time_category import (
    MOCCSTimeCategory,
)


class mo_ccs_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Missouri Child Care Subsidy monthly sliding fee"
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://web.archive.org/web/20211208060516id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2025/010",
        "https://dese.mo.gov/sites/dese/files/media/pdf/2025/10/10.2025%20Income%20Eligibility%20Table%20%282%29.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs.copay
        adjusted_income = spm_unit("mo_ccs_adjusted_income", period)

        # The sliding fee tier is read from the household-size ladder by
        # monthly adjusted gross income (5 CSR 25-200.060(3)(C)1). Households
        # larger than the largest published size (20) use the largest size
        # column.
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = 20
        tier = select(
            [size == n for n in range(1, max_size)],
            [
                getattr(p.tier, f"size_{n}").calc(adjusted_income)
                for n in range(1, max_size)
            ],
            default=getattr(p.tier, f"size_{max_size}").calc(adjusted_income),
        )

        # The daily fee per child depends on the tier and the child's care
        # time unit (full, half, or part).
        person = spm_unit.members
        time_category = person("mo_ccs_time_category", period)
        full_fee = p.daily_fee.full_unit.calc(tier)
        half_fee = p.daily_fee.half_unit.calc(tier)
        part_fee = p.daily_fee.part_unit.calc(tier)
        # tier is an SPMUnit-level array; broadcast to people via their unit.
        daily_fee = select(
            [
                time_category == MOCCSTimeCategory.FULL_TIME,
                time_category == MOCCSTimeCategory.HALF_TIME,
                time_category == MOCCSTimeCategory.PART_TIME,
            ],
            [
                spm_unit.project(full_fee),
                spm_unit.project(half_fee),
                spm_unit.project(part_fee),
            ],
        )

        # Children with a special need or in protective services are not charged
        # a sliding fee (Manual 2025.010; 5 CSR 25-200.060(3)(C)4). A Protective
        # Service Child is a child with special needs per 5 CSR 25-200.050(11),
        # so foster / protective-services children are also waived.
        is_eligible_child = person("mo_ccs_eligible_child", period)
        is_disabled = person("is_disabled", period.this_year)
        is_protective = person("is_in_foster_care", period) | person(
            "receives_or_needs_protective_services", period.this_year
        )
        days = person("childcare_attending_days_per_month", period.this_year)
        in_care = is_eligible_child & ~is_disabled & ~is_protective & (days > 0)
        monthly_fee = spm_unit.sum(daily_fee * days * in_care)

        # Households whose only income is Temporary Assistance, or whose gross
        # income is below the state median income floor, pay only the minimum
        # annual fee. The 25% SMI floor is keyed on gross income (Manual
        # 2025.010 item 3), unlike the sliding fee tier above.
        gross_income = spm_unit("mo_ccs_countable_income", period)
        smi = spm_unit("hhs_smi", period.this_year)
        smi_floor = smi * p.smi_minimum_rate / MONTHS_IN_YEAR
        is_tanf = spm_unit("is_tanf_enrolled", period)
        pays_minimum = is_tanf | (gross_income < smi_floor)
        minimum_fee = p.minimum_annual_fee / MONTHS_IN_YEAR
        return where(pays_minimum, minimum_fee, monthly_fee)
