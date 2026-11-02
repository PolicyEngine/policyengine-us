from policyengine_us.model_api import *


class nc_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina additions to the adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2020 D-400 Schedule S, Part A, line 16: above-the-line qualified
        # charitable contribution deduction.
        "https://www.ncdor.gov/documents/files/2020-d-400-schedule-s-web/open#page=2",
    )
    defined_for = StateCode.NC

    adds = ["nc_other_additions", "charitable_contributions_ald"]
