from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ms_medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Mississippi Medicaid parent income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MS
    # PDF pages 1-10.
    reference = "https://medicaid.ms.gov/wp-content/uploads/2026/03/Appendix-A-3-MAGI-Income-Limits.-2014-to-present.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.medicaid.parent.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        reference_instant = period.start.offset(
            int(p.annual_reference_month) - 1, "month"
        )
        published = parameters(reference_instant).gov.states.ms.dom.medicaid.parent
        monthly_limit = published.income_limit.amount[capped_size]
        state_group = person.household("state_group_str", period)
        annual_fpg = fpg(size, state_group, period, parameters)
        # COE-075's combined column already includes the five-point disregard.
        # Normalize the literal whole-dollar table amount without adding it
        # again. The shared financial helper's ceiling is then idempotent.
        # Annual comparisons use the current year's March table, not the
        # prior-year table legally applicable in January and February.
        source_limit = monthly_limit * MONTHS_IN_YEAR / annual_fpg
        # The source's explicit disregard chart stops at the verified maximum.
        # Preserve the existing national ratio for larger households rather
        # than capping their legal income standard to the last listed size.
        legacy_limit = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        return where(
            size <= p.max_household_size,
            source_limit,
            legacy_limit.income_limit["MS"],
        )
