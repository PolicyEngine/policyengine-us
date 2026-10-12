from policyengine_us.model_api import *


class ca_sbd_general_relief_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for San Bernardino County General Relief due to immigration status"
    )
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://wp.sbcounty.gov/tad/wp-content/uploads/sites/25/2025/06/gr000101-4.pdf#page=2",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief.eligibility
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        return np.isin(immigration_status_str, p.qualified_immigration_status)
