from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ga.dfcs.liheap.eligibility._ga_liheap_housing import (
    ga_liheap_has_direct_payment_route,
)


class ga_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Georgia LIHEAP ordinary eligibility"
    defined_for = StateCode.GA
    # State plan pages 5, 8, 9, 30; manual pages 3, 50, 56, 57, 75, 89.
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ga_liheap_household_size", period)
        income = spm_unit("ga_liheap_income", period)
        limit = spm_unit("ga_liheap_income_limit", period)
        heating_type = spm_unit("heating_type", period)
        heating_expense = spm_unit("heating_expense", period)
        # Explicit heating responsibility can qualify with no current bill.
        # A positive primary bill also establishes burden with heat in rent,
        # including subsidized housing. The rent flag alone is insufficient.
        energy_burden = (
            spm_unit("has_heating_expense", period)
            | (heating_expense > 0)
            | ga_liheap_has_direct_payment_route(spm_unit, period)
        )
        # Pure-assistance categorical eligibility requires actual receipt by
        # every member and assistance-only income/resources. Aggregate TANF/SNAP
        # inputs cannot establish those facts, so this uses the ordinary test.
        # Account credits of $1,000+ and administrative household exclusions
        # also need unavailable inputs; the selected heating account is assumed
        # to satisfy those rules. Annual expense is not an account-credit proxy.
        return (
            (size > 0)
            & (income <= limit)
            & energy_burden
            & (heating_type != heating_type.possible_values.NONE)
        )
