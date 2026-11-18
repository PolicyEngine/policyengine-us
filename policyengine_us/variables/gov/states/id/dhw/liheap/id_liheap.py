from policyengine_us.model_api import *


class id_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP regular heating assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "id_liheap_eligible"
    reference = (
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.payment
        cost = spm_unit("id_liheap_estimated_heating_cost", period)
        income = spm_unit("id_liheap_countable_income", period)
        # Zero income has the highest burden.
        burden_group = select(
            [
                cost >= income * p.energy_burden.high_rate,
                cost >= income * p.energy_burden.medium_rate,
            ],
            [3, 2],
            default=1,
        )
        # Safe lookup; eligibility already requires a known area.
        area = clip(spm_unit("id_liheap_heating_area", period), 1, 3)
        heating = spm_unit("heating_type", period)
        types = heating.possible_values
        chart_amount = select(
            [
                (heating == types.ELECTRICITY) | (heating == types.SOLAR),
                heating == types.NATURAL_GAS,
                (heating == types.FUEL_OIL)
                | (heating == types.KEROSENE)
                | (heating == types.PROPANE),
                (heating == types.COAL) | (heating == types.WOOD),
            ],
            [
                p.matrix.electricity[area][burden_group],
                p.matrix.natural_gas[area][burden_group],
                p.matrix.oil_or_propane[area][burden_group],
                p.matrix.coal_or_wood[area][burden_group],
            ],
            default=0,
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        person = spm_unit.members
        # Annual age stands in for age by the end of the program year.
        age = person("age", period)
        vulnerable = (
            (age < p.target_bonus.child_age_limit)
            | (age >= p.target_bonus.elderly_age)
            | person("is_disabled", period)
        )
        qualified = person("is_citizen_or_legal_immigrant", period)
        target_bonus = spm_unit.any(vulnerable & qualified) * p.target_bonus.amount
        # The chart's $122 minimum and $1,285 maximum are its own lowest and
        # highest amounts, so no separate limits apply.
        return where(heat_in_rent, p.rent, chart_amount) + target_bonus
