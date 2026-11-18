from policyengine_us.model_api import *


class nh_ssp_disability_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets New Hampshire APTD medical criteria"
    definition_period = YEAR
    defined_for = StateCode.NH
    reference = "https://gc.nh.gov/rsa/html/XII/167/167-6.htm"
    documentation = """
    State medical eligibility requires federal disability criteria and the
    state's 48-month impairment-duration test. The formula identifies people
    already reported permanently and totally disabled. Set the state decision
    explicitly for qualifying impairments of finite duration.
    """
    # NOTE: is_permanently_and_totally_disabled is an input that defaults to
    # false, so microsimulation pays Aid to the Permanently and Totally Disabled
    # only where the dataset sets it; Old Age Assistance and Aid to the Needy
    # Blind do not depend on it.

    def formula(person, period, parameters):
        return person("meets_ssi_disability_criteria", period) & person(
            "is_permanently_and_totally_disabled", period
        )
