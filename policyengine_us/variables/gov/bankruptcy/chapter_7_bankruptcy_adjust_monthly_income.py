from policyengine_us.model_api import *


class chapter_7_bankruptcy_adjust_monthly_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Adjust monthly income"
    definition_period = MONTH
    reference = (
        "https://www.uscourts.gov/sites/default/files/form_b122a-1.pdf#page=1",
        "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=1",
    )
    documentation = "Line 4 in form 122A-2"

    def formula(spm_unit, period, parameters):
        employment_income = add(spm_unit, period, ["irs_employment_income"])
        alimony_income = add(spm_unit, period, ["alimony_income"])
        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )
        business_and_farm_income = add(
            spm_unit, period, ["partnership_s_corp_income", "farm_income"]
        )
        rental_income = add(
            spm_unit, period, ["farm_rent_income", "rental_income"]
        )
        interest_and_dividends_income = add(
            spm_unit, period, ["divident_income", "interest_income"]
        )
        unemployment_compensation = add(
            spm_unit, period, ["unemployment_compensation"]
        )
        pension_and_retirement_income = add(
            spm_unit, period, ["pension_income", "retirement_distribution"]
        )
        total = (
            employment_income
            + alimony_income
            + child_support_received
            + business_and_farm_income
            + rental_income
            + interest_and_dividends_income
            + unemployment_compensation
            + pension_and_retirement_income
        )
        return total / MONTHS_IN_YEAR
