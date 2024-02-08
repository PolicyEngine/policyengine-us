from policyengine_us.model_api import *


class oh_lump_sum_distribution_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio lump sum distribution credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29",
    )

    adds = ["oh_lump_sum_distribution_credit_person"]
