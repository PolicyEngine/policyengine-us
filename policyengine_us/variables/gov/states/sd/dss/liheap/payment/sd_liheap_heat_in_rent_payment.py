from policyengine_us.model_api import *


class sd_liheap_heat_in_rent_payment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP heat-in-rent payment component"
    defined_for = StateCode.SD
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:41.02",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SD_BenefitMatrix_2026.pdf",
        # Physical pages 31-32: October-April payments and tenant rent share.
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=31",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.payment.heat_in_rent
        region = spm_unit("sd_liheap_region", period)
        supported_region = (region >= 1) & (region <= 4)
        maximum = p.amount[clip(region, 1, 4)]
        # Existing Person rent is the net tenant share, apportioned after modeled
        # HUD assistance. Report observed rent directly, or override the existing
        # housing_assistance amount, when that default is not actual receipt.
        annual_rent = max_(add(spm_unit, period, ["rent"]), 0)
        cap = annual_rent / MONTHS_IN_YEAR * p.months * p.rent_share
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_type = spm_unit("heating_type", period)
        has_heat = heating_type != heating_type.possible_values.NONE
        # The fuel-neutral heat-in-rent schedule permits unknown primary fuel;
        # no separate heating bill is required. Subsidy does not disqualify a
        # positive tenant share, while zero share yields zero through the cap.
        # sd_liheap applies supported eligibility. This annual estimate assumes
        # seven eligible months of steady rent and completed landlord verification;
        # prior payments, changes in rent, and tribal routing are not observed.
        return where(
            supported_region & heat_in_rent & has_heat,
            min_(maximum, cap),
            0,
        )
