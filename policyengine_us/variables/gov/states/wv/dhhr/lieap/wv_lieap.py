from policyengine_us.model_api import *


class wv_lieap(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia modeled regular heating LIEAP payment"
    unit = USD
    definition_period = YEAR
    defined_for = "wv_lieap_income_eligible"
    reference = (
        # PDF pages 1729-1731,1753-1755,1772-1773
        "https://bfa.wv.gov/media/39948/download?inline=#page=1729",
        # PDF pages 1730-1734,1757-1758,1775-1776
        "https://bfa.wv.gov/media/40005/download?inline=#page=1730",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.lieap.payment
        size = spm_unit("wv_lieap_household_size", period)
        income = spm_unit("wv_lieap_countable_income", period) / MONTHS_IN_YEAR
        # Approved convention: use the printed upper bounds continuously,
        # including cents, rather than the overlapping integer lower bounds.
        band = p.income_band.calc(income, right=True)
        # Exact compression of every occupied published cell, not extrapolation.
        # Income eligibility confines sizes 1-20 to occupied table cells.
        base = p.base_amount + p.amount_step * (size - 1 - band)
        heating = spm_unit("heating_type", period)
        types = heating.possible_values
        multiplier = select(
            [
                heating == types.ELECTRICITY,
                heating == types.NATURAL_GAS,
                (heating == types.FUEL_OIL)
                | (heating == types.KEROSENE)
                | (heating == types.PROPANE)
                | (heating == types.WOOD)
                | (heating == types.COAL),
            ],
            [
                p.fuel_multiplier.electricity,
                p.fuel_multiplier.natural_gas,
                p.fuel_multiplier.bulk_fuel,
            ],
            default=0,
        )
        # Integer bases and three-decimal multipliers give exact dollar mills.
        # Convert those to cents half up, matching the printed $70.79/$147.02.
        mills = np.rint(base * multiplier * 1_000)
        amount = np.floor((mills + 5) / 10) / 100
        pays_for_heat = spm_unit("has_heating_expense", period)
        # Above 20 members is unmodeled coverage, not legal ineligibility.
        # Existing heating-cost facts approximate the documented obligation;
        # designated rent charges and some dwelling facts remain unobserved.
        return where((size <= p.max_household_size) & pays_for_heat, amount, 0)
