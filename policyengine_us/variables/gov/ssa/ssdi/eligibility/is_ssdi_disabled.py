from policyengine_us.model_api import *


class is_ssdi_disabled(Variable):
    value_type = bool
    entity = Person
    label = "Is disabled for SSDI purposes"
    definition_period = YEAR
    reference = "https://www.ssa.gov/benefits/disability/qualify.html"
    documentation = """
    A person is considered disabled for SSDI if:
    1. They cannot engage in substantial gainful activity (SGA)
    2. The condition has lasted or is expected to last at least 12 months or result in death
    3. They cannot do work they did before or adjust to other work
    """

    def formula(person, period, parameters):
        # Per 42 USC 423(d), disability determination requires:
        # - Medical evaluation of physical/mental impairments
        # - Vocational assessment of ability to perform past or other work
        # - Duration requirement (12+ months or expected death)
        #
        # Since PolicyEngine lacks access to medical records and vocational
        # assessments, we use input variables as proxies for the full
        # disability determination process.
        #
        # Note: Unlike is_ssi_disabled, this does NOT check SGA status.
        # For SSDI, SGA is checked separately in is_ssdi_eligible.
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)
        return is_disabled | is_blind
