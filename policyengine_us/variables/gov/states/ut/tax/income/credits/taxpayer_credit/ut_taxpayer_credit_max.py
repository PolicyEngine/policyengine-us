from policyengine_us.model_api import *


class ut_taxpayer_credit_max(Variable):
    """
    Line 16 on Utah 2022 Individual Income Tax return form TC-40.
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxpayer credit maximum"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        gov = parameters(period).gov
        ut_taxpayer_credit = gov.states.ut.tax.income.credits.taxpayer_credit
        count_dependents = tax_unit("tax_unit_count_dependents", period)
        personal_exemption = (
            count_dependents * ut_taxpayer_credit.personal_exemption
        )

        itemizes = tax_unit("tax_unit_itemizes", period)
        us_standard_deduction = tax_unit("standard_deduction", period)
        deductions_if_itemizing = gov.irs.deductions.deductions_if_itemizing
        deductions_if_itemizing = [
            deduction
            for deduction in deductions_if_itemizing
            if deduction
            not in [
                "salt_deduction",
                # Exclude QBID to avoid circular reference.
                "qualified_business_income_deduction",
            ]
        ]
        us_itemized_deductions_less_salt = add(
            tax_unit, period, deductions_if_itemizing
        )

        total_deductions = personal_exemption + where(
            itemizes, us_itemized_deductions_less_salt, us_standard_deduction
        )

        return total_deductions * ut_taxpayer_credit.rate
