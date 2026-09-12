from policyengine_us.model_api import *


class heating_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost"
    unit = USD
    definition_period = YEAR
    documentation = "Heating costs attributed to this tax unit for the Michigan home heating credit. Set this amount directly to the claimant's actual costs billed from November 1 of the previous year through October 31 of the claim year, including secondary heating fuels. For a known heating type, the default approximates these costs using the SPM unit's primary-fuel bill only when it contains one tax unit. With multiple tax units, costs default to zero because the shared bill does not identify each claimant's share. UNSPECIFIED heating types retain the legacy sum of heating_expense_person."
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-527a",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-7-Book.pdf#page=5",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040CR-7-Book.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        spm_unit = tax_unit.spm_unit
        heating_type = spm_unit("heating_type", period)
        unspecified = heating_type == heating_type.possible_values.UNSPECIFIED
        shared_heating_expense = spm_unit("heating_expense", period)
        # Count tax units in the SPM unit; these are not necessarily the
        # eligible Michigan claimants or everyone sharing the dwelling.
        tax_units_in_spm_unit = add(spm_unit, period, ["is_tax_unit_head"])
        sole_tax_unit = tax_units_in_spm_unit == 1
        # A shared bill is not any one claimant's cost; callers supply
        # each claimant's share directly.
        canonical = where(sole_tax_unit, shared_heating_expense, 0)
        # Deprecated legacy adapter for households that do not use the
        # canonical heating inputs.
        legacy = add(tax_unit, period, ["heating_expense_person"])
        return where(unspecified, legacy, canonical)
