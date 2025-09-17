from policyengine_us.model_api import *


class state_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "State standard deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # States that adopt the federal standard deduction
        # Based on comments in state_standard_deductions.yaml
        FEDERAL_STANDARD_DEDUCTION_STATES = [
            "CT",  # Connecticut
            "ID",  # Idaho
            "ME",  # Maine
            "MO",  # Missouri
            "ND",  # North Dakota
            "NM",  # New Mexico
            "SC",  # South Carolina
            "UT",  # Utah
            "CO",  # Colorado
        ]

        # Get the sum of state-specific standard deductions
        state_specific = add(
            tax_unit,
            period,
            parameters(period).gov.states.household.state_standard_deductions,
        )

        # Get the current state
        state_code = tax_unit.household("state_code_str", period)

        # Check if the state adopts federal standard deduction
        uses_federal = np.isin(state_code, FEDERAL_STANDARD_DEDUCTION_STATES)

        # Get federal standard deduction
        federal_deduction = tax_unit("standard_deduction", period)

        # Return federal deduction for states that adopt it, otherwise state-specific
        return where(uses_federal, federal_deduction, state_specific)
