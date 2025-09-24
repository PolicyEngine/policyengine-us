from policyengine_us.model_api import *


class state_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "State adjusted gross income"
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_agis"

    def formula(tax_unit, period, parameters):
        # States that adopt the federal AGI
        # Based on comments in state_agis.yaml
        FEDERAL_AGI_STATES = [
            "CO",  # Colorado
            "MI",  # Michigan
            "MN",  # Minnesota
            "NC",  # North Carolina
            "ND",  # North Dakota
            "NM",  # New Mexico
            "SC",  # South Carolina
        ]

        # Get the current state
        state_code = tax_unit.household("state_code_str", period)

        # Get the sum of state-specific AGIs
        state_specific_base = add(
            tax_unit,
            period,
            parameters(period).gov.states.household.state_agis,
        )

        # Special handling for states that have separate individual and joint AGI calculations
        # Arkansas and Delaware use different AGI calculations based on filing status
        STATES_WITH_INDIVIDUAL_JOINT_AGI = {
            "AR": {
                "indiv": "ar_agi_indiv",
                "joint": "ar_agi_joint",
            },
            "DE": {
                "indiv": "de_agi_indiv",
                "joint": "de_agi_joint",
            },
        }

        # Calculate maximum AGI for states with individual/joint distinction
        # This ensures we use the higher of the two calculations
        for state, variables in STATES_WITH_INDIVIDUAL_JOINT_AGI.items():
            is_state = state_code == state
            indiv_agi = add(tax_unit, period, [variables["indiv"]])
            joint_agi = add(tax_unit, period, [variables["joint"]])
            max_agi = max_(indiv_agi, joint_agi)
            state_specific_base = where(is_state, max_agi, state_specific_base)

        # Check if the state adopts federal AGI
        uses_federal = np.isin(state_code, FEDERAL_AGI_STATES)

        # Get federal AGI
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Return federal AGI for states that adopt it, otherwise state-specific
        return where(uses_federal, federal_agi, state_specific_base)
