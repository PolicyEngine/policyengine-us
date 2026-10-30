from policyengine_us.model_api import *


class mo_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP Energy Assistance"
    documentation = "Missouri's one-time regular heating Energy Assistance payment for the fuel the household selects, taken as the largest of three amounts: the amount for the fuel of its own heating bill; the electric amount for its electric supplier account when the home has heating; and, for an unsubsidized renter whose heat is included in the rent, the rent share of annual rent up to the amount for its heating fuel. The regular monthly rental charge is pre_subsidy_rent, since only unsubsidized renters receive the rent share. A home with no heating or an unspecified heating fuel receives no electric amount. Verified for FY2026-FY2027; earlier years use model parameter backfilling and are unverified historical estimates. Energy Crisis Intervention Program (ECIP) crisis payments are excluded."
    reference = (
        # PDF pages 2-4
        "https://web.archive.org/web/20250603190025/https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MO_BenefitMatrix_2026.docx",
        # PDF pages 1, 3
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/02/liheap-application.pdf#page=1",
        # PDF pages 51, 62-63, 129
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=51",
    )
    defined_for = "mo_liheap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        fuel_amount = p.amount[heating_type]
        own_fuel_amount = where(spm_unit("has_heating_expense", period), fuel_amount, 0)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        annual_rent = add(spm_unit, period, ["pre_subsidy_rent"])
        renter_amount = where(
            heat_in_rent & ~subsidized,
            min_(annual_rent * p.rent_share, fuel_amount),
            0,
        )
        heats_home = (heating_type != types.NONE) & (heating_type != types.UNSPECIFIED)
        electric_bill = spm_unit("pre_subsidy_electricity_expense", period)
        electric_amount = where(
            heats_home & (electric_bill > 0), p.amount.ELECTRICITY, 0
        )
        # The household selects the fuel to be paid (2025 manual page 51).
        return max_(max_(own_fuel_amount, renter_amount), electric_amount)
