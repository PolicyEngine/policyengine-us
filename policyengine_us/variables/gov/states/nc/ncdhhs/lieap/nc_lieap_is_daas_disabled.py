from policyengine_us.model_api import *


class nc_lieap_is_daas_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets North Carolina LIEAP DAAS disability criteria"
    documentation = (
        "Whether the person receives Division of Aging and Adult Services "
        "services and meets EP-300.02's disability-benefit definition: receiving "
        "SSI, Social Security disability, or Veterans Administration disability. "
        "Both service receipt and the disability-benefit condition are required. "
        "This reported fact is not inferred from generic disability or Medicaid."
    )
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=1,2,10"
    )
