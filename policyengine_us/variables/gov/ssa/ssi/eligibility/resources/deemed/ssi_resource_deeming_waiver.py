from policyengine_us.model_api import *


class ssi_resource_deeming_waiver(Variable):
    value_type = bool
    entity = Person
    label = "Child meets the SSI resource deeming home care exception"
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)(2)"
    )
    documentation = """
    Adjudicated exception under 20 CFR 416.1202(b)(2). All three conditions
    must hold: the disabled child previously received reduced SSI in a
    medical treatment facility under 416.414; qualifies for Medicaid home
    care under 1915(c) or 1902(e)(3); and would otherwise be ineligible due
    to parental income or resource deeming. Medicaid enrollment alone does
    not establish this exception. Supply the determination for each month.
    """
