from policyengine_us.model_api import *


class wi_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin TANF"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/148",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/07/"
        "7.4.1_Community_Service_Jobs_(CSJ).htm",
    )
    defined_for = StateCode.WI
    documentation = """
    Wisconsin Works (W-2) provides fixed monthly payments based on
    placement type, NOT based on family size or income level.

    Unlike traditional TANF programs that use a benefit reduction
    formula (Max Benefit - Countable Income), Wisconsin provides the
    same payment amount to all eligible families in a given placement
    type, regardless of family size or actual income level (as long as
    income is below 115% FPL).

    Placement types and monthly payments:
    - Community Service Job (CSJ): $653/month
    - W-2 Transition (W-2 T): $608/month
    - Custodial Parent of Infant (CMC): $673/month
    - At Risk Pregnancy (ARP): $673/month

    This simplified implementation assumes CSJ placement ($653/month)
    for all eligible families. Actual benefit depends on W-2 agency
    placement assignment based on employment readiness assessment.

    NOTE: Cannot model placement assignment criteria (employment
    barriers, work capacity, medical incapacity) in PolicyEngine's
    single-period architecture. Cannot model sanctions for
    non-participation.
    """

    def formula(spm_unit, period, parameters):
        # Determine eligibility
        eligible = spm_unit("wi_tanf_eligible", period)

        # Get CSJ payment standard (most common placement type)
        p = parameters(period).gov.states.wi.dcf.tanf
        payment_amount = p.payment_standard

        # Return fixed payment if eligible, otherwise $0
        # No benefit reduction formula - payment is fixed
        return where(eligible, payment_amount, 0)
