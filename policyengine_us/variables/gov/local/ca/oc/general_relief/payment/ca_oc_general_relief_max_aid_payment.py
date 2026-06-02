from policyengine_us.model_api import *


class ca_oc_general_relief_max_aid_payment(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Orange County General Relief maximum aid payment"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = (
        "https://www.ochealthinfo.com/sites/hca/files/2021-07/DUI%20Program%20Standards%20%28FINAL%29%207.2021.pdf#page=32",
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=04",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.oc.general_relief.payment
        # The MAP is based on the size of the GR Economic Unit and its housing
        # arrangement (Sec 80.2.d). It covers only the aided persons: children
        # and members excluded for SSI/other cash assistance or immigration
        # status are not included in the MAP.
        size = spm_unit("ca_oc_general_relief_aided_person_count", period)
        capped_size = clip(size, 1, 10)
        base = p.max_aid_payment[capped_size]
        # The MAP is reduced when the Economic Unit shares housing with one or
        # more people who are not part of the unit (Sec 80.3.a(3)). We proxy the
        # number of other people sharing the home as the household members
        # outside the Economic Unit (the SPM unit).
        household_size = spm_unit.household("household_size", period.this_year)
        unit_size = spm_unit("spm_unit_size", period.this_year)
        other_people = max_(household_size - unit_size, 0)
        reduction = p.shared_housing_reduction.calc(other_people)
        return base * (1 - reduction)
