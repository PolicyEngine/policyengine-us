from policyengine_us.model_api import *


class mn_eap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Minnesota EAP Primary Heat benefit"
    documentation = (
        "Primary Heat is the single regular benefit of Minnesota's Energy "
        "Assistance Program. It pays a share of the household's total home "
        "energy cost, including non-heating electricity, between the minimum "
        "and maximum benefit. Verified for FFY2026 and FFY2027; earlier years "
        "use model parameter backfilling and are unverified historical "
        "estimates. Crisis, Energy Related Repair and weatherization are out "
        "of scope."
    )
    defined_for = "mn_eap_eligible"
    reference = (
        # PDF pages 117, 124-126
        "https://mn.gov/commerce-stat/pdfs/ffy26-eap-policy-manual.pdf#page=117",
        # PDF pages 119, 126-128
        "https://mn.gov/commerce-stat/pdfs/ffy27-eap-policy-manual.pdf#page=119",
        "https://liheapch.acf.gov/docs/2026/state-plans/MN_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MN_BenefitMatrix_2026.xlsx",
        "https://mn.gov/commerce-stat/xls/phb-calculator.xlsx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.commerce.eap.payment
        cost = spm_unit("mn_eap_energy_cost", period)
        share = spm_unit("mn_eap_pay_share", period)
        # Appendix 4A rounds the share times cost to whole dollars with Excel
        # ROUND (halves away from zero), then applies the floor and ceiling.
        # The floor applies at any positive cost; households without a cost
        # basis (no backup matrix row) receive nothing.
        amount = np.floor(share * cost + 0.5)
        return where(cost > 0, clip(amount, p.minimum, p.maximum), 0)
