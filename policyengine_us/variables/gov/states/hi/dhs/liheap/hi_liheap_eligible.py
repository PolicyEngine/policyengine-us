from policyengine_us.model_api import *


class hi_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii LIHEAP regular heating assistance"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # PDF pages 5, 9
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=5",
        # PDF pages 1, 3
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=1",
        # Draft FY2026 manual sections 1.4, 2.1, 2.8, 2.12, 4.2 and 5.5.
        # PDF pages 57-58, 60-61, 65, 67
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=57",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        income = spm_unit("hi_liheap_countable_income", period)
        limit = spm_unit("hi_liheap_income_limit", period)
        # Draft manual 5.5 reads "equal to or less than"; draft 2.9 and the matrix
        # read "less than" and "below". The calculation section is followed.
        income_eligible = income <= limit
        # Any member's receipt qualifies. Plan vs manual: draft 2.8 and the matrix
        # add general assistance and AABD to the plan's SNAP, SSI and TANF, and the
        # manual is followed. AABD and the DHS-case match have no input, and SSA's
        # independent-living certification is not read. Annual receipt stands in
        # for the first day of the application month.
        person = spm_unit.members
        receives_ssi = spm_unit.any(
            (person("ssi", period, options=[ADD]) > 0)
            | (add(person, period, ["receives_ssi"]) > 0)
        )
        categorical = receives_ssi | (
            add(spm_unit, period, ["snap", "tanf", "general_assistance"]) > 0
        )
        # Both manuals pay gas as heating and electricity as cooling, and a household
        # asks to have one utility credited (2.12; application Q17). So any home's
        # gas bill qualifies, whatever heats it or the rent includes. Bottled gas does
        # not show the active utility account that draft 2.1 requires. Callers must
        # send heating_type.
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        gas_bill = spm_unit("gas_expense", period) > 0
        # Draft 2.1 and 4.2 and application Q23-24 accept a share of utilities in
        # rent, which has no input; plan 2.3 and the 2020 manual do not.
        responsible = (gas_bill & (fuel != types.UNSPECIFIED)) | (
            heat_in_rent & (fuel == types.NATURAL_GAS)
        )
        return (size > 0) & (income_eligible | categorical) & responsible
