from policyengine_us.model_api import *


class ssdi_family_maximum(Variable):
    value_type = float
    entity = Person
    label = "SSDI family maximum benefit"
    unit = USD
    definition_period = MONTH
    reference = "https://www.ssa.gov/oact/cola/familymax.html"
    documentation = """
    Maximum total benefit payable to a disabled worker's family.
    For disability cases, typically 85% of AIME but not less than 100%
    or more than 150% of the worker's PIA.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssdi.family_maximum

        aime = person("ssdi_aime", period.this_year)
        monthly_aime = aime / 12  # Convert annual to monthly
        pia = person("ssdi_pia", period)

        # Base calculation: 85% of monthly AIME
        family_max = monthly_aime * p.percentage

        # Apply min and max constraints based on PIA
        family_max = max_(family_max, pia * p.min_percentage)
        family_max = min_(family_max, pia * p.max_percentage)

        return family_max
