from policyengine_us.model_api import *


class az_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arizona LIHEAP"
    documentation = (
        "Annual Arizona Standard LIHEAP benefit, paid once per 12-month "
        "eligibility period from the benefit matrix points: $160 for up to 4 "
        "points, $320 for 5 to 8, $480 for 9 to 12 and $640 for 13 or more. "
        "It covers heating and cooling energy bills alike and is not capped at "
        "the bill. Verified for FY2026; earlier years use model parameter "
        "backfilling and are unverified historical estimates. Crisis "
        "assistance, water for evaporative cooling, weatherization and the "
        "Senior Utility Assistance Program recertification maximum are not "
        "modeled."
    )
    defined_for = "az_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AZ_BenefitMatrix_Heating_2026.pdf#page=1",
        # PDF pages 4, 10
        "https://liheapch.acf.gov/docs/2026/state-plans/AZ_Plan_2026.pdf#page=4",
        # PDF pages 10, 29-30, 33-34
        "https://des.az.gov/sites/default/files/dl/CCSD-LIHEAP-Policy.pdf#page=10",
        "https://des.az.gov/liheap",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap.payment
        points = spm_unit("az_liheap_points", period)
        # Section VII.B.3.b.iii.D.2: if all vendor accounts "have been paid in
        # full by their LIHEAP benefit and there is a remaining benefit, this
        # benefit will be allocated to the highest priority" account, so the
        # payment is the matrix amount, not the bill. The plan's heating
        # (16.80%) and cooling (38.12%) components are funding shares of this
        # single Standard benefit, not separate household payments.
        return p.amount.calc(points)
