from policyengine_us.model_api import *


class ssdi_individual_benefit(Variable):
    value_type = float
    entity = Person
    label = "SSDI individual benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://www.ssa.gov/benefits/disability/"
    documentation = """
    Individual SSDI benefit amount after waiting period.
    Equals the Primary Insurance Amount (PIA) for eligible individuals.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssdi

        is_eligible = person("is_ssdi_eligible", period.this_year)
        pia = person("ssdi_pia", period)

        # Check if waiting period is complete
        months_waiting = person("ssdi_months_waiting", period.this_year)
        waiting_period_complete = months_waiting >= p.waiting_period

        # Benefit is PIA if eligible and waiting period complete
        return where(is_eligible & waiting_period_complete, pia, 0)
