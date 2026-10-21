from policyengine_us.model_api import *


class sd_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP regular heating assistance"
    defined_for = "sd_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SD_BenefitMatrix_2026.pdf",
        "https://liheapch.acf.gov/docs/2026/state-plans/SD_Plan_2026.pdf#page=22",
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:40",
        "https://sdlegislature.gov/Rules/Administrative/67:15:01:43.01",
        # PDF pages 2, 4
        "https://dss.sd.gov/formsandpubs/docs/ENERGY/energyassistanceapplication.pdf#page=2",
        # PDF pages 30-32
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=30",
    )

    def formula(spm_unit, period, parameters):
        base_payment = spm_unit("sd_liheap_base_payment", period)
        heating_type = spm_unit("heating_type", period)
        fuels = heating_type.possible_values
        # Plan item 9.1 (FY2024 and FY2025 page 21, FY2026 page 22) pays heating
        # assistance directly to energy suppliers, with these exceptions only:
        # "If household uses coal or wood as it's primary heat source or a
        # household's heat is included in rent, a payment is issued directly to
        # the household." Rule 67:15:01:40 names only wood or coal, rule
        # 67:15:01:43.01 pays "the energy supplier or landlord", and application
        # EA-297 (page 4) asks for a supplier fill ticket for "Fuel Oil/Kerosene"
        # and pays only "Heat in Rent, Wood, or Coal" to the household. Manual
        # page 31 (2018) pays kerosene "the entire benefit amount" by check; the
        # plan and rules supersede it, so kerosene is capped like fuel oil.
        cash_payment = (heating_type == fuels.WOOD) | (heating_type == fuels.COAL)
        # heating_expense is read as unpaid eligible seasonal charges, not bills
        # already paid or an unrestricted annual total. Gas and electric meter
        # reads: October 1-May 15; propane and oil fills: July 1-April 30. The
        # inputs do not show charge dates or balances.
        expense = max_(spm_unit("heating_expense", period), 0)
        direct_payment = where(cash_payment, base_payment, min_(base_payment, expense))
        # Heat-in-rent uses a steady tenant share for all seven eligible months;
        # changes in rent, already-paid months and prior awards are not tracked.
        # Unpriced fuels remain outside coverage.
        return where(
            spm_unit("heat_expense_included_in_rent", period),
            spm_unit("sd_liheap_heat_in_rent_payment", period),
            direct_payment,
        )
