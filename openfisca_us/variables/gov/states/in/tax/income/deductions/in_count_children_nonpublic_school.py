from openfisca_us.model_api import *


class in_count_children_nonpublic_school(Variable):
    value_type = int
    entity = TaxUnit
    label = "IN count children nonpublic school"
    definition_period = YEAR
    documentation = "Number of dependent children who attended a nonpublic school in Indiana for 180 days or more and for whom non-reimbursed education expenditures were made."
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4" #(d)(1)
    )
