from policyengine_us.model_api import *


class ga_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP heating matrix amount"
    defined_for = StateCode.GA
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.payment
        size = spm_unit("ga_liheap_household_size", period)
        income = spm_unit("ga_liheap_income", period)
        # The published lower-income thresholds end at size 16. Capping this
        # lookup is provisional for larger units, not verified policy coverage.
        lookup_size = clip(size, 1, p.maximum_table_size)
        lower_income = income <= p.lower_income_limit[lookup_size]
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        base = select(
            [
                heating_type == fuel.ELECTRICITY,
                heating_type == fuel.NATURAL_GAS,
                heating_type == fuel.FUEL_OIL,
                heating_type == fuel.PROPANE,
                heating_type == fuel.WOOD,
            ],
            [
                p.base_amount.electricity,
                p.base_amount.natural_gas,
                p.base_amount.fuel_oil,
                p.base_amount.propane,
                p.base_amount.wood,
            ],
            default=0,
        )
        # This is an ungated schedule amount with no cap at the reported bill.
        # Unpriced kerosene, coal, solar, other, and unspecified fuels return an
        # incomplete zero estimate; this is not a legal ineligibility finding.
        return where(base > 0, base + lower_income * p.lower_income_uplift, 0)
