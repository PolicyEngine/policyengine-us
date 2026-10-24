from policyengine_us.model_api import *


class mo_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP Energy Assistance"
    documentation = "Missouri's one-time regular heating Energy Assistance payment: the amount for the household's primary heating fuel, or for a renter household whose heat is included in the rent, the rent share of annual rent up to that amount. The regular monthly rental charge is pre_subsidy_rent, since only unsubsidized renters with heat in rent are eligible. Verified for FY2026-FY2027; earlier years use model parameter backfilling and are unverified historical estimates. Energy Crisis Intervention Program (ECIP) crisis payments are excluded."
    reference = (
        # PDF pages 2-4
        "https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MO_BenefitMatrix_2026.docx",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/02/liheap-application.pdf#page=1",
        # PDF pages 62-63, 129
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=62",
    )
    defined_for = "mo_liheap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap
        heating_type = spm_unit("heating_type", period)
        fuel_amount = p.amount[heating_type]
        annual_rent = add(spm_unit, period, ["pre_subsidy_rent"])
        renter_amount = min_(annual_rent * p.rent_share, fuel_amount)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        return where(heat_in_rent, renter_amount, fuel_amount)
