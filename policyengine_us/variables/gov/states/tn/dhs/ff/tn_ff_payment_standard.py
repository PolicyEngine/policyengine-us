from policyengine_us.model_api import *


class tn_ff_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First payment standard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Determine assistance unit size
        p = parameters(period).gov.states.tn.dhs.ff.payment
        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_family_size)

        # # Determine if eligible for DGPA
        # # DGPA eligibility: caretaker is at/above age threshold, disabled,
        # # provides care for disabled, or no eligible adults present
        # person = spm_unit.members
        # age = person("age", period)
        # is_disabled = person("is_disabled", period)

        # dgpa_age_threshold = p.payment.dgpa.age_threshold
        # caretaker_meets_age = spm_unit.any(age >= dgpa_age_threshold)
        # caretaker_is_disabled = spm_unit.any(is_disabled)
        # # For simplification, assume eligible for DGPA if caretaker meets age or is disabled
        # eligible_for_dgpa = caretaker_meets_age | caretaker_is_disabled

        # # Get SPA and DGPA amounts
        # spa = p.payment.standard_payment_amount[capped_size]
        # dgpa = p.payment.dgpa.amount[capped_size]

        # # Return DGPA if eligible, otherwise SPA
        # return where(eligible_for_dgpa, dgpa, spa)

        # Simplified: return SPA only (DGPA disabled for now)
        return p.standard_payment_amount[capped_size]
