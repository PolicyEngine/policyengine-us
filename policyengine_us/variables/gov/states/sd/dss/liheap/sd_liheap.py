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
        "https://dss.sd.gov/formsandpubs/docs/ENERGY/energyassistanceapplication.pdf#page=2",
        # Physical pages 30-32: vendor claims, rent payments, and cash fuels.
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/SD_Policy-and-Procedures-Manual2018.pdf#page=30",
    )

    def formula(spm_unit, period, parameters):
        base_payment = spm_unit("sd_liheap_base_payment", period)
        heating_type = spm_unit("heating_type", period)
        fuels = heating_type.possible_values
        # The historical manual pays these fuels' full award to the household.
        # The current application groups kerosene with oil for the price only.
        cash_payment = (
            (heating_type == fuels.WOOD)
            | (heating_type == fuels.COAL)
            | (heating_type == fuels.KEROSENE)
        )
        # Approved input assumption: heating_expense represents unpaid eligible
        # seasonal charges, not already-paid bills or an unrestricted annual
        # total. Gas/electric meter dates: October 1-May 15; propane/oil fills:
        # July 1-April 30. Existing inputs cannot establish those dates/balances.
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
