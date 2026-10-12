from policyengine_us.model_api import *


class vt_aabd_ep_resources_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Vermont Essential Person resource eligibility"
    definition_period = MONTH
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf"
    documentation = "SSI/AABD receipt automatically passes the resource test. For state-only applicants, explicitly supply the resource determination under rule 2785, including Reach Up resource exclusions as of August 2024, Medicaid limits, and nonspouse dependent proration."

    def formula(person, period, parameters):
        received = person("ssi", period) + person("vt_aabd_federal", period)
        return person.marital_unit.any(received > 0)
