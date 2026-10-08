from policyengine_us.model_api import *


class sd_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for South Dakota LIEAP within the modeled household scope"
    defined_for = StateCode.SD
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:01",
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:09",
        # Sections 1.4a and 17.3: SNAP recipients and qualified noncitizens.
        "https://liheapch.acf.gov/docs/2026/state-plans/SD_Plan_2026.pdf",
        # PDF pages 9, 17
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        # Manual physical page 9: "Mixed households are eligible for assistance."
        # At least one citizen or eligible alien must be in the household.
        has_qualified_member = spm_unit("sd_liheap_household_size", period) > 0
        income = spm_unit("sd_liheap_countable_income", period)
        limit = spm_unit("sd_liheap_income_limit", period)
        # All application members must receive SNAP for categorical income
        # eligibility. January receipt and SNAP unit size approximate a stable
        # application-month caseload; a benefit for only some members is not
        # enough. A member ineligible for SNAP, such as an ineligible alien,
        # sends the household to the income worksheet (physical page 17), so
        # SNAP unit size is compared with every member.
        receives_snap = spm_unit("snap", period.first_month) > 0
        all_receive_snap = (
            spm_unit("snap_unit_size", period.first_month)
            == spm_unit("spm_unit_size", period)
        ) & receives_snap
        income_eligible = (income <= limit) | all_receive_snap
        heating_type = spm_unit("heating_type", period)
        has_heat = heating_type != heating_type.possible_values.NONE
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        responsible_for_heat = where(
            heat_in_rent,
            add(spm_unit, period, ["rent"]) > 0,
            spm_unit("has_heating_expense", period),
        )
        # Assume an independent, noninstitutional household served by the state,
        # with required heating/landlord verification and no duplicate tribal
        # award. Existing inputs cannot establish tribal service-area routing,
        # institutional residence, or completed administrative verification.
        return has_qualified_member & income_eligible & has_heat & responsible_for_heat
