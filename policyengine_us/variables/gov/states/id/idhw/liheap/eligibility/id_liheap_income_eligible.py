from policyengine_us.model_api import *


class id_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP income eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = (
        "Whether household meets Idaho LIHEAP income requirements (60% SMI)"
    )
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.85",
    ]

    def formula(spm_unit, period, parameters):
        # Get household income and size
        income = spm_unit("id_liheap_income", period)
        household_size = spm_unit.nb_persons()

        # Get income limits from parameters
        p = parameters(period).gov.states.id.idhw.liheap.income_limit

        # Handle household sizes up to 7 using 60% SMI parameters
        # For sizes 8+, Idaho uses 150% FPG
        income_limit = select(
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
            # For sizes 8+: use 150% FPG monthly from parameters
            default=p.eight_plus_person,
        )

        return income <= income_limit
