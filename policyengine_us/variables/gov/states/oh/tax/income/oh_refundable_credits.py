from policyengine_us.model_api import *


class oh_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio refundable credits"
    reference = (
        # 2021 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf",
        # 2022 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf",
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
