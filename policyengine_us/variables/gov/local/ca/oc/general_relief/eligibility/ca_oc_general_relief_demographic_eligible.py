from policyengine_us.model_api import *


class ca_oc_general_relief_demographic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets Orange County General Relief demographic requirements"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = (
        "https://www.ssa.ocgov.com/cash-calfresh/faqs/general-relief",
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=02",
    )

    def formula(spm_unit, period, parameters):
        # General Relief aids adults without minor children. A unit with a minor
        # child is effectively routed to CalWORKs, and the parent cannot also
        # receive GR: the unit must apply for any aid it appears eligible for or
        # be ineligible (Sec 20, "Failure ... to apply for any aid ... results
        # in ineligibility"); a parent receiving CalWORKs is an excluded member
        # (Sec 20.4.b); and a parent who has exhausted the CalWORKs time limit
        # is excluded from the GR MAP until all children turn 18 (Sec 80.2.d).
        # So no realistic family has a child on CalWORKs and that child's parent
        # on GR. The rare non-parent-caretaker case is not modeled.
        p = parameters(period).gov.local.ca.oc.general_relief.eligibility
        age = spm_unit.members("monthly_age", period)
        return spm_unit.all(age >= p.adult_age_threshold)
