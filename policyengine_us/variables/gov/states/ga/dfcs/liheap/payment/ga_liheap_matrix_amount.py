from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ga.dfcs.liheap.eligibility._ga_liheap_housing import (
    ga_liheap_has_direct_payment_route,
)


class ga_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Georgia LIHEAP heating matrix amount"
    defined_for = StateCode.GA
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/GA_BenefitMatrix_Heat-Cool_2026.pdf",
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=30",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=89",
    )

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
        base_amounts = [
            p.base_amount.electricity,
            p.base_amount.natural_gas,
            p.base_amount.fuel_oil,
            p.base_amount.propane,
            p.base_amount.wood,
        ]
        base = select(
            [
                heating_type == fuel.ELECTRICITY,
                heating_type == fuel.NATURAL_GAS,
                heating_type == fuel.FUEL_OIL,
                heating_type == fuel.PROPANE,
                heating_type == fuel.WOOD,
            ],
            base_amounts,
            default=0,
        )
        # Applicant payments use the lowest award in the income level.
        direct_payment = ga_liheap_has_direct_payment_route(spm_unit, period)
        base = where(
            direct_payment & (heating_type != fuel.NONE),
            np.minimum.reduce(base_amounts),
            base,
        )
        # This is an ungated schedule amount with no cap at the reported bill.
        # Ordinary vendor payments for unpriced kerosene, coal, solar, other,
        # and unspecified fuels return an incomplete zero estimate; this is
        # not a legal ineligibility finding.
        return where(base > 0, base + lower_income * p.lower_income_uplift, 0)
