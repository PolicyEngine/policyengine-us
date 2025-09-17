from policyengine_us.model_api import *


class state_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "State itemized deductions"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_itemized_deductions"

    def formula(tax_unit, period, parameters):
        # States that adopt the federal itemized deductions
        # Based on comments in state_itemized_deductions.yaml
        FEDERAL_ITEMIZED_DEDUCTION_STATES = [
            "CT",  # Connecticut
            "GA",  # Georgia
            "ND",  # North Dakota
            "SC",  # South Carolina
            "UT",  # Utah
        ]

        # Get the sum of state-specific itemized deductions
        state_specific = add(
            tax_unit,
            period,
            parameters(period).gov.states.household.state_itemized_deductions,
        )

        # Get the current state
        state_code = tax_unit.household("state_code_str", period)

        # Check if the state adopts federal itemized deductions
        uses_federal = np.isin(state_code, FEDERAL_ITEMIZED_DEDUCTION_STATES)

        # Get federal itemized deductions (sum of all federal itemized deduction components)
        federal_itemized = add(
            tax_unit,
            period,
            parameters(period).gov.irs.deductions.itemized_deductions,
        )

        # Return federal itemized deductions for states that adopt them, otherwise state-specific
        return where(uses_federal, federal_itemized, state_specific)
