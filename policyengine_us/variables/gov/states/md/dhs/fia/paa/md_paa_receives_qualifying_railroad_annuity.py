from policyengine_us.model_api import *


class md_paa_receives_qualifying_railroad_annuity(Variable):
    value_type = bool
    entity = Person
    label = (
        "Receives a railroad annuity for age, blindness or disability for Maryland PAA"
    )
    definition_period = MONTH
    defined_for = StateCode.MD
    default_value = False
    documentation = (
        "Set to true for a month when the applicant receives a Railroad Retirement "
        "Board annuity for age, blindness or disability. Enter the annuity dollars "
        "in railroad_benefits."
    )
    reference = "https://regs.maryland.gov/us/md/exec/comar/07.03.07.03"
