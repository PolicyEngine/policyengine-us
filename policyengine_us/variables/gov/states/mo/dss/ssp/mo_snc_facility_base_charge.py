from policyengine_us.model_api import *


class mo_snc_facility_base_charge(Variable):
    value_type = float
    entity = Person
    label = "Missouri SNC facility base charge"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MO
    reference = (
        "https://dssmanuals.mo.gov/supplemental-nursing-care/0610-000-00/0610-025-00/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2020/10/im-72.pdf",
    )
