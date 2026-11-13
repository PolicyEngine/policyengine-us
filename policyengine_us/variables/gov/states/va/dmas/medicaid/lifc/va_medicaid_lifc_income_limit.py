from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class va_medicaid_lifc_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Virginia Medicaid LIFC income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://www.dmas.virginia.gov/media/0aynyhxk/m04-1-1-26a.pdf#page=51",
        "https://www.dmas.virginia.gov/media/2249/transmittal-dmas-5-effective-07-1-2017.pdf#page=35",
        "https://www.dmas.virginia.gov/media/2245/transmittal-dmas-9-effective-7-1-18-signed.pdf#page=34",
        "https://www.dmas.virginia.gov/media/2258/tn-dmas-13-effective-7-1-2019.pdf#page=42",
        "https://www.dmas.virginia.gov/media/2254/tn-dmas-17-effective-7-1-20.pdf#page=59",
        "https://www.ecfr.gov/current/title-42/section-435.603#p-435.603(d)(4)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.dmas.medicaid.lifc.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)

        group1_limit = (
            p.group1.main[capped_size] + additional_people * p.group1.additional
        )
        group2_limit = (
            p.group2.main[capped_size] + additional_people * p.group2.additional
        )
        group3_limit = (
            p.group3.main[capped_size] + additional_people * p.group3.additional
        )

        locality_group = person.household("va_medicaid_lifc_locality_group", period)
        groups = locality_group.possible_values
        income_limit = select(
            [
                locality_group == groups.GROUP_I,
                locality_group == groups.GROUP_II,
                locality_group == groups.GROUP_III,
            ],
            [group1_limit, group2_limit, group3_limit],
            default=group1_limit,
        )
        state_group = person.household("state_group_str", period)
        return income_limit / fpg(size, state_group, period, parameters)

    def formula_2018(person, period, parameters):
        income_limit = va_medicaid_lifc_income_limit.formula(person, period, parameters)
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        return income_limit + p.fpl_disregard

    def formula_2021(person, period, parameters):
        # Retain the existing calculation outside the 2018-2020 correction.
        return va_medicaid_lifc_income_limit.formula(person, period, parameters)
