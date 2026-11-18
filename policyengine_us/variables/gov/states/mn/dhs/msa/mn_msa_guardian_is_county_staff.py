from policyengine_us.model_api import *


class mn_msa_guardian_is_county_staff(Variable):
    value_type = bool
    default_value = False
    entity = Person
    label = "Whether the person's Minnesota Supplemental Aid guardian or conservator is a member of the county agency staff"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = "https://www.revisor.mn.gov/statutes/cite/256D.44#stat.256D.44.5"
