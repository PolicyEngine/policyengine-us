from policyengine_us.model_api import *


class ca_liheap_utility_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP utility heating eligibility"
    defined_for = StateCode.CA
    reference = (
        # PDF pages 9,182-184,193,202-203,205,219,221,264-265,279,363
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=9",
        # PDF pages 189,233-234
        "https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=189",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        utility_heat = np.isin(
            heating_type.decode_to_str(), p.eligibility.utility_heating_fuels
        )
        known_fuel = (heating_type != types.NONE) & (heating_type != types.UNSPECIFIED)
        utility_bills = add(
            spm_unit, period, ["pre_subsidy_electricity_expense", "gas_expense"]
        )
        # The applicant names the utility account that takes the benefit, so a
        # home heated with another fuel qualifies on a gas or electric bill.
        utility_account = utility_heat | (known_fuel & (utility_bills > 0))
        # A household receives one HEAP or WPO payment per program year.
        other_component = (
            add(
                spm_unit,
                period,
                ["ca_liheap_covered_liquid_heating", "ca_liheap_wood_heating"],
            )
            > 0
        )
        # Madera denies applicants below its minimum. Only its priority plan was
        # recovered, and a home with no burden group has no points to test.
        burden_group = spm_unit("ca_liheap_energy_burden_group", period)
        points = spm_unit("ca_liheap_madera_priority_points", period)
        meets_priority = (burden_group == 0) | (points >= p.local.madera.minimum_points)
        return (
            spm_unit("ca_liheap_basic_eligible", period)
            & utility_account
            & ~other_component
            & meets_priority
        )
