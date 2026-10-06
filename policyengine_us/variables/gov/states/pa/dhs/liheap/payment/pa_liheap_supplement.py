from policyengine_us.model_api import *


class pa_liheap_supplement(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP vulnerable household heating supplement"
    defined_for = StateCode.PA
    # OPS 25-08-01 (August 2025) and OPS 26-07-01 (July 2026), pages 1-2, govern
    # the two issuances; both state the same vulnerability criteria on page 2.
    reference = (
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/assets/docs/2024-2025%20Low-Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29%20Supplemental%20Payments.pdf#page=1",
        "http://services.dpw.state.pa.us/oimpolicymanuals/liheap/assets/docs/2025-2026%20Low-Income%20Home%20Energy%20Assistance%20Program%20%28LIHEAP%29.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.payment.supplement
        eligible = spm_unit("pa_liheap_eligible", period)
        age = spm_unit.members("age", period)
        disabled_or_blind = spm_unit.members("is_disabled", period) | spm_unit.members(
            "is_blind", period
        )
        disability_assistance = (
            (spm_unit.members("social_security_disability", period) > 0)
            | (spm_unit.members("disability_benefits", period) > 0)
            | ((spm_unit.members("ssi", period, options=[ADD]) > 0) & disabled_or_blind)
        )
        # Aggregate veterans benefits do not identify disability assistance.
        # A disability flag alone does not establish the required cash receipt.
        vulnerable = spm_unit.any(
            (age >= p.elderly_age) | (age < p.child_age_limit) | disability_assistance
        )
        # Both memos use under five; the July 30, 2026 news release instead
        # says under six. This component follows the issuance directives.
        # Annual eligibility approximates actual prior Cash-grant receipt.
        # Existing inputs do not identify application-date age or address
        # changes after payment; assume the household retains its residence.
        # Do not condition receipt on the separately unverified matrix bounds.
        return eligible * vulnerable * p.amount
