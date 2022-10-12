from policyengine_us.model_api import *


class in_nol_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN net operating loss add back"
    definition_period = YEAR
    documentation = (
        "Add back for net operating losses reported on federal Schedule 1."
    )
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(16)
    # use federal variables if they are added later
