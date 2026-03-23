from policyengine_us.model_api import *


class local_occupational_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local occupational tax"
    documentation = (
        "Local employee occupational and head taxes, aggregated from "
        "jurisdiction-specific rules."
    )
    unit = USD

    adds = [
        "co_denver_employee_occupational_privilege_tax",
        "co_glendale_employee_occupational_privilege_tax",
        "co_greenwood_village_employee_occupational_privilege_tax",
        "co_sheridan_employee_occupational_privilege_tax",
    ]
