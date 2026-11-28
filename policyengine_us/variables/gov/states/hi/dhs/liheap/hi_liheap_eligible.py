from policyengine_us.model_api import *


class hi_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Hawaii LIHEAP regular heating or cooling assistance"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        # PDF pages 5,9,12
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=5",
        # FY2027 plan 1.4.
        "https://liheapch.acf.gov/docs/2027/state-plans/HI_Plan_2027.pdf#page=5",
        # PDF pages 1, 3
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=1",
        # Draft FY2026 manual Energy Credit definition and sections 1.4, 2.1, 2.8,
        # 2.12, 4.2 and 5.5.
        # PDF pages 55, 57-58, 60-61, 65, 67
        "https://humanservices.hawaii.gov/wp-content/uploads/2025/07/Model-Plan-Packet-2026.pdf#page=55",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        income = spm_unit("hi_liheap_countable_income", period)
        limit = spm_unit("hi_liheap_income_limit", period)
        p = parameters(period).gov.states.hi.dhs.liheap.eligibility
        # Draft FY2026 manual 5.5 reads "equal to or less than"; draft 2.9 and the
        # matrix read "less than" and "below". The calculation section is
        # followed. Every FY2027 text requires income below the limit.
        if p.income_at_limit_eligible:
            income_eligible = income <= limit
        else:
            income_eligible = income < limit
        # The FY2027 plan ends categorical eligibility from October 2026.
        categorical = False
        if p.categorical_in_effect:
            # Any member's receipt qualifies. Plan vs manual: draft 2.8 and the
            # matrix add general assistance and AABD to the plan's SNAP, SSI and
            # TANF, and the manual is followed. AABD and the DHS-case match have
            # no input, and SSA's independent-living certification is not read.
            # Annual receipt stands in for the first day of the application
            # month.
            person = spm_unit.members
            receives_ssi = spm_unit.any(
                (person("ssi", period) > 0)
                | (add(person, period, ["receives_ssi"]) > 0)
            )
            categorical = receives_ssi | (
                add(spm_unit, period, ["snap", "tanf", "general_assistance"]) > 0
            )
        # The Energy Credit goes to one gas or electricity account (draft 2.12
        # and application Q17). The model uses a gas or electric bill and a
        # known heating fuel to establish utility responsibility. Reported PV
        # status determines whether the additional net-usage requirement applies.
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        gas_bill = spm_unit("gas_expense", period) > 0
        electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        # The draft's Energy Credit definition, 2.1 and 4.2 and application Q23-24
        # accept a share of utilities in rent, "electric/gas" alike. Utilities in
        # rent (tenant_pays_utilities false) qualify any known fuel, and gas or
        # electric heat in rent qualifies too. The size of the share has no input,
        # and a third-party payer or a rent-free home is not identified.
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period)
        rent_fuel = (fuel == types.NATURAL_GAS) | (fuel == types.ELECTRICITY)
        responsible = (
            (gas_bill | electric_bill | utilities_in_rent) & (fuel != types.UNSPECIFIED)
        ) | (heat_in_rent & rent_fuel)
        # Draft 2.12 and 4.2 require billed usage in excess of generation.
        # Account fees can make a PV household's bill positive without net use.
        pv_status = spm_unit("hi_liheap_photovoltaic_status", period)
        pv_eligible = pv_status != pv_status.possible_values.PV_WITHOUT_NET_USAGE
        return (size > 0) & (income_eligible | categorical) & responsible & pv_eligible
