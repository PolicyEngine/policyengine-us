from policyengine_us.model_api import *


class vt_aabd_ep_resources_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Vermont Essential Person resource eligibility"
    definition_period = MONTH
    # PDF pages 46-47
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=46"
    documentation = "SSI/AABD receipt automatically passes the resource test. For state-only applicants, explicitly supply the resource determination under rule 2785, including Reach Up resource exclusions as of August 2024, Medicaid limits, and nonspouse dependent proration."

    def formula(person, period, parameters):
        receives = (
            (person("ssi", period) > 0)
            | person("receives_ssi", period)
            | (person("vt_aabd_federal", period) > 0)
        )
        return person.marital_unit.any(receives)
