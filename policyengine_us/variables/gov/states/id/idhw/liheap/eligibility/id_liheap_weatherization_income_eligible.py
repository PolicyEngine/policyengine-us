from policyengine_us.model_api import *
from numpy import select


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

        # Use simplified 200% FPL monthly limits by household size
        household_size = spm_unit.nb_persons()

        # Approximate 200% FPL monthly limits for 2025
        fpl_200_monthly = select(
            [
                household_size == 1,
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
            ],
            [
                2_600,  # 1 person
                3_520,  # 2 people
                4_433,  # 3 people
                5_350,  # 4 people
                6_267,  # 5 people
                7_183,  # 6 people
            ],
            default=8_100,  # 7+ people
        )

        return income <= fpl_200_monthly
