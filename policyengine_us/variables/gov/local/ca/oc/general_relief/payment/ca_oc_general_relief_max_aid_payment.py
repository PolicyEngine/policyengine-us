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
        # arrangement (Sec 80.2.d). It covers only the eligible persons: children
        # and members excluded for SSI/other cash assistance or immigration
        # status are not included in the MAP.
        size = spm_unit("ca_oc_general_relief_eligible_person_count", period)
        capped_size = clip(size, 1, 10)
        base = p.max_aid_payment[capped_size]
        # The MAP is reduced when the Economic Unit shares housing with one or
        # more people who are not part of the unit (Sec 80.3.a(3)). The reduction
        # does not apply to individuals placed in Housing Support Programs who may
        # receive a shelter subsidy; we proxy that exemption with receipt of
        # housing assistance, since we don't track Housing Support Program
        # placement at the moment.
        is_shared_living = spm_unit.household("is_shared_living", period)
        exempt = spm_unit("receives_housing_assistance", period.this_year)
        reduction = where(is_shared_living & ~exempt, p.shared_housing_reduction, 0)
        return base * (1 - reduction)
