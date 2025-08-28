from policyengine_us.model_api import *


class az_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona LIHEAP income eligible"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.az.des.liheap

        # Get monthly income (LIHEAP uses gross income)
        annual_income = spm_unit("az_liheap_countable_income", period)
        monthly_income = annual_income / 12

        # Get household size
        household_size = spm_unit.nb_persons()

        # Get income limit for household size, capped at 8
        household_size_capped = min_(household_size, 8)
        
        # Access parameter using select for different household sizes
        income_limit = select(
            [
                household_size_capped == 1,
                household_size_capped == 2,
                household_size_capped == 3,
                household_size_capped == 4,
                household_size_capped == 5,
                household_size_capped == 6,
                household_size_capped == 7,
                household_size_capped == 8,
            ],
            [
                p.income_limits["1"],
                p.income_limits["2"],
                p.income_limits["3"],
                p.income_limits["4"],
                p.income_limits["5"],
                p.income_limits["6"],
                p.income_limits["7"],
                p.income_limits["8"],
            ],
        )

        return monthly_income <= income_limit
