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
        state_code = tax_unit.household("state_code_str", period)

        # Special handling for states that need individual vs joint standard deduction maximum
        STATES_WITH_INDIVIDUAL_JOINT_MAXIMUM = {
            "MT": {
                "indiv": "mt_standard_deduction_indiv",
                "joint": "mt_standard_deduction_joint",
            },
            "IA": {
                "indiv": "ia_standard_deduction_indiv",
                "joint": "ia_standard_deduction_joint",
            },
            "DE": {
                "indiv": "de_standard_deduction_indv",
                "joint": "de_standard_deduction_joint",
            },
            "AR": {
                "indiv": "ar_standard_deduction_indiv",
                "joint": "ar_standard_deduction_joint",
            },
            "MS": {
                "indiv": "ms_standard_deduction_indiv",
                "joint": "ms_standard_deduction_joint",
            },
            "KY": {
                "indiv": "ky_standard_deduction_indiv",
                "joint": "ky_standard_deduction_joint",
            },
        }

        # Calculate maximum standard deductions for applicable states
        for state, variables in STATES_WITH_INDIVIDUAL_JOINT_MAXIMUM.items():
            is_state = state_code == state
            indiv_deductions = add(tax_unit, period, [variables["indiv"]])
            joint_deductions = add(tax_unit, period, [variables["joint"]])
            max_deductions = max_(indiv_deductions, joint_deductions)
            state_specific = where(is_state, max_deductions, state_specific)

        # Check if the state adopts federal standard deduction
        uses_federal = np.isin(state_code, FEDERAL_STANDARD_DEDUCTION_STATES)

        # Get federal standard deduction
        federal_deduction = tax_unit("standard_deduction", period)

        # Return federal deduction for states that adopt it, otherwise state-specific
        return where(uses_federal, federal_deduction, state_specific)
