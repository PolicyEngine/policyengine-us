from policyengine_us.model_api import *


class tn_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20",
        "Tennessee Administrative Code § 1240-01-50-.20 - Standard of Need/Income",
        "Tennessee TANF State Plan 2024-2027",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Determine assistance unit size
        unit_size = spm_unit.nb_persons()
        p = parameters(period).gov.states.tn.dhs.tanf.benefit
        # Cap unit size at maximum defined in parameters
        max_size = 10
        capped_size = min_(unit_size, max_size)

        # Determine if eligible for DGPA
        # DGPA eligibility: caretaker is 60+, disabled, provides care for disabled,
        # or no eligible adults present
        person = spm_unit.members
        age = person("age", period)
        is_disabled = person("is_disabled", period)

        caretaker_is_60_or_older = spm_unit.any(age >= 60)
        caretaker_is_disabled = spm_unit.any(is_disabled)
        # For simplification, assume eligible for DGPA if caretaker is 60+ or disabled
        eligible_for_dgpa = caretaker_is_60_or_older | caretaker_is_disabled

        # Get SPA and DGPA amounts
        spa = p.standard_payment_amount[capped_size]
        dgpa = p.differential_grant_payment_amount[capped_size]

        # Return DGPA if eligible, otherwise SPA
        return where(eligible_for_dgpa, dgpa, spa)
