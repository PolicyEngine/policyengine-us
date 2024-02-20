from policyengine_us.model_api import *


class mi_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan homestead property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34",
    )
    defined_for = "mi_homestead_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        allowable_credit_amount = tax_unit(
            "mi_homestead_property_tax_credit_pre_alternate_senior_amount",
            period,
        )
        senior_credit_amount = tax_unit(
            "mi_homestead_property_tax_credit_alternate_senior_amount", period
        )
        return max_(allowable_credit_amount, senior_credit_amount)
