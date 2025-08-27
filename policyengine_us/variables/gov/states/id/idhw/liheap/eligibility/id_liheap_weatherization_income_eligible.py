from policyengine_us.model_api import *


class id_liheap_weatherization_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP weatherization income eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household meets income requirements for weatherization (200% FPL)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83",
    ]

    def formula(spm_unit, period, parameters):
        # Weatherization uses 200% FPL instead of 60% SMI
        income = spm_unit("id_liheap_income", period)

        # Get income limits from parameters
        household_size = spm_unit.nb_persons()
        p = parameters(
            period
        ).gov.states.id.idhw.liheap.weatherization_income_limit

        # Use 200% FPL monthly limits by household size from parameters
        fpl_200_monthly = select(
            [
                household_size == 1,
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
                household_size == 7,
            ],
            [
                p.one_person,
                p.two_person,
                p.three_person,
                p.four_person,
                p.five_person,
                p.six_person,
                p.seven_person,
            ],
            default=p.eight_plus_person,  # 8+ people
        )

        return income <= fpl_200_monthly
