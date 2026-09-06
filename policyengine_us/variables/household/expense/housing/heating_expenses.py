from policyengine_us.model_api import *


class heating_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit heating cost"
    unit = USD
    definition_period = YEAR
    documentation = "The tax unit's share of the dwelling's annual heating cost, used by the Michigan home heating credit. Michigan allows one credit per claimant and spouse, and single adults sharing a home may each claim, so the SPM unit's heating_expense is split evenly across the tax units living there. Households whose heating_type is UNSPECIFIED keep the pre-canonical person-level sum of heating_expense_person."
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-527a",
        "https://www.michigan.gov/taxes/iit/tax-guidance/credits-exemptions/home-heating-credit/home-heating-credit-and-shared-housing-situations",
    )

    def formula(tax_unit, period, parameters):
        spm_unit = tax_unit.spm_unit
        heating_type = spm_unit("heating_type", period)
        unspecified = heating_type == heating_type.possible_values.UNSPECIFIED
        dwelling_heating_expense = spm_unit("heating_expense", period)
        # Each tax unit has one head, so counting heads counts the tax units
        # that share the dwelling.
        spm_unit_tax_units = add(spm_unit, period, ["is_tax_unit_head"])
        # Avoid an array divide-by-zero warning by not using where().
        share = np.zeros_like(dwelling_heating_expense)
        mask = spm_unit_tax_units > 0
        share[mask] = dwelling_heating_expense[mask] / spm_unit_tax_units[mask]
        # Deprecated legacy adapter for households that do not use the
        # canonical heating inputs.
        legacy = add(tax_unit, period, ["heating_expense_person"])
        return where(unspecified, legacy, share)
