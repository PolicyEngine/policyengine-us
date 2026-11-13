from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wy_medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Wyoming Medicaid Family Care income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.WY
    reference = (
        "https://health.wyo.gov/wp-content/uploads/2019/01/SFY-2018-Wyoming-Medicaid-Annual-Report.pdf#page=95",
        "https://www.govinfo.gov/content/pkg/CFR-2017-title42-vol4/pdf/CFR-2017-title42-vol4-sec435-603.pdf#page=2",
    )

    def formula(person, period, parameters):
        parent = parameters(period).gov.states.wy.health.medicaid.parent
        legacy = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        legacy_limit = legacy.income_limit["WY"]
        if not parent.in_effect:
            return legacy_limit

        p = parent.income_limit
        size = person("medicaid_household_size", period)
        lookup_size = clip(size, p.min_household_size, p.max_household_size).astype(int)
        state_group = person.household("state_group_str", period)
        annual_fpg = fpg(size, state_group, period, parameters)
        # Preserve the shared annual-FPG/whole-dollar comparison convention;
        # this does not reconstruct Wyoming's April FPG adoption or cents.
        source_limit = (
            p.amount[lookup_size] * MONTHS_IN_YEAR / annual_fpg + p.fpl_disregard
        )
        verified_size = (size >= p.min_household_size) & (size <= p.max_household_size)
        return where(verified_size, source_limit, legacy_limit)
