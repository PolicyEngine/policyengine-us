from policyengine_us.model_api import *


class de_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP regular heating assistance"
    defined_for = "de_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.de.dhss.liheap.payment
        # Other-state rows have a zero band; keep all vectorized lookups valid.
        band = max_(spm_unit("de_liheap_income_band", period), 1)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        matrix_amount = select(
            [
                heat_in_rent | (fuel == types.ELECTRICITY),
                fuel == types.PROPANE,
                (fuel == types.FUEL_OIL) | (fuel == types.KEROSENE),
                fuel == types.NATURAL_GAS,
                (fuel == types.WOOD) | (fuel == types.COAL) | (fuel == types.OTHER),
            ],
            [
                p.matrix.electricity[band],
                p.matrix.propane[band],
                p.matrix.oil[band],
                p.matrix.natural_gas[band],
                p.matrix.other[band],
            ],
            default=0,
        )
        subsidized = spm_unit("receives_housing_assistance", period)
        # rent is the tenant's share after housing assistance, in annual units.
        rent = add(spm_unit, period, ["rent"])
        flat_benefit = (
            subsidized
            & ~heat_in_rent
            & (rent <= p.subsidized_rent_ceiling * MONTHS_IN_YEAR)
        )
        # Published matrix amounts already incorporate statewide heating-cost
        # evidence. No additional household bill cap or priority supplement
        # is imposed on the regular heating award in the verified sources.
        return where(flat_benefit, p.subsidized_amount, matrix_amount)
