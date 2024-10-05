from policyengine_us.model_api import *


class oh_tax_before_joint_filing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio tax liability before the joint filing credit"
    reference = (
        # 2021 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf",
        # 2022 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf",
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit(
            "oh_income_tax_before_non_refundable_credits", period
        )
        total_credits = tax_unit("oh_partial_non_refundable_credits", period)
        return max_(0, tax_before_credits - total_credits)
