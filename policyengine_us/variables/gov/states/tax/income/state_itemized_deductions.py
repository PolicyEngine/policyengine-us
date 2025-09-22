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

        # Get the current state
        state_code = tax_unit.household("state_code_str", period)

        # Get the sum of state-specific itemized deductions
        state_specific_base = add(
            tax_unit,
            period,
            parameters(period).gov.states.household.state_itemized_deductions,
        )

        # Special handling for states that need individual vs joint itemization maximum
        STATES_WITH_INDIVIDUAL_JOINT_MAXIMUM = {
            "MT": {
                "indiv": "mt_itemized_deductions_for_federal_itemization_indiv",
                "joint": "mt_itemized_deductions_for_federal_itemization_joint",
            },
            "IA": {
                "indiv": "ia_itemized_deductions_indiv",
                "joint": "ia_itemized_deductions_joint",
            },
            "DE": {
                "indiv": "de_itemized_deductions_indv",
                "joint": "de_itemized_deductions_joint",
            },
            "AR": {
                "indiv": "ar_itemized_deductions_indiv",
                "joint": "ar_itemized_deductions_joint",
            },
        }

        # Calculate maximum itemized deductions for applicable states
        for state, variables in STATES_WITH_INDIVIDUAL_JOINT_MAXIMUM.items():
            is_state = state_code == state
            indiv_deductions = add(tax_unit, period, [variables["indiv"]])
            joint_deductions = add(tax_unit, period, [variables["joint"]])
            max_deductions = max_(indiv_deductions, joint_deductions)
            state_specific_base = where(
                is_state, max_deductions, state_specific_base
            )

        # Check if the state adopts federal itemized deductions
        uses_federal = np.isin(state_code, FEDERAL_ITEMIZED_DEDUCTION_STATES)

        # Get federal itemized deductions (sum of all federal itemized deduction components)
        federal_itemized = add(
            tax_unit,
            period,
            parameters(period).gov.irs.deductions.itemized_deductions,
        )

        # Return federal itemized deductions for states that adopt them, otherwise state-specific
        return where(uses_federal, federal_itemized, state_specific_base)
