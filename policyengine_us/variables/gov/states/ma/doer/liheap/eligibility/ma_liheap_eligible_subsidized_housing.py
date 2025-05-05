from policyengine_us.model_api import *


class ma_liheap_eligible_subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP eligible subsidized housing"
    reference = "https://liheapch.acf.hhs.gov/tables/FY2015/subsidize.htm#MA"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.doer.liheap.threshold
        income = add(spm_unit, period, ["irs_gross_income"])
        rent_threshold = income * p.rent_rate
        person = spm_unit.members
        rent_person = person("rent", period)
        total_rent = spm_unit.sum(rent_person)
        is_subsidized = spm_unit("receives_housing_assistance", period)
        rent_eligible = total_rent > rent_threshold
        heat_in_rent = spm_unit("heat_costs_included_in_rent", period)

        return (is_subsidized & heat_in_rent & rent_eligible) | (
            is_subsidized & ~heat_in_rent
        )
