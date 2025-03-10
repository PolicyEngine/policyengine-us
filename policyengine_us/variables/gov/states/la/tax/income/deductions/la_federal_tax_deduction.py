from policyengine_us.model_api import *


class la_federal_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana federal tax deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",  # 2022 repealed
        "https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3",  # 2021 line 9
        "https://law.justia.com/codes/louisiana/2021/revised-statutes/title-47/rs-298/",  # (3)
    ]
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        tax_before_refundable_credits = tax_unit(
            "income_tax_before_refundable_credits", period
        )
        # The deduction is also reduced by the ACA PTC repayment amount.
        # We do not model this as it depends on the advance PTC received throughout the year.
        reductions = add(
            tax_unit,
            period,
            ["form_4972_lumpsum_distributions"],
        )
        amount = max_(0, tax_before_refundable_credits - reductions)

        # The deduction was discontinued in 2022
        p = parameters(period).gov.states.la.tax.income.deductions.federal_tax
        return amount * p.availability
