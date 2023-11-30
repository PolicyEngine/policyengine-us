from policyengine_us.model_api import *


class mt_modified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana modified income for the taxable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2110/",
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6",
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=6",
    )
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.adjustments.social_security
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        # Line 1 take all ss benefits
        net_benefits = tax_unit.sum(
            person("social_security", period) * is_head_or_spouse
        )  # Line1
        # Line 2 multiply benefits by a fraction
        halved_benefits = net_benefits * p.fraction.income
        # Line 3 subtract taxable ss benefits from gross income
        gross_income = tax_unit.sum(
            person("irs_gross_income", period) * is_head_or_spouse
        )
        taxable_social_security = tax_unit.sum(
            person("taxable_social_security", period) * is_head_or_spouse
        )
        # gross_income always equal or greater than taxable_social_security
        # because grosee_income includes taxable_social_security and other items
        reduced_gross_income = gross_income - taxable_social_security
        # Line 4 - All montana additions reduced by interest and mutual fund dividends
        # from state, country, or municipal bonds from other states and addition to taxable social security benefits
        # this is currently not included in the model, so we process with the
        # total value of mt_other_additions
        additions = tax_unit("mt_other_additions", period)
        # Line 5 tax exempt interest income
        tax_exempt_interest_income = tax_unit.sum(
            person("tax_exempt_interest_income", period) * is_head_or_spouse
        )
        adds = (
            halved_benefits
            + reduced_gross_income
            + additions
            + tax_exempt_interest_income
        )  # Line 6
        above_the_line_deductions = tax_unit(
            "above_the_line_deductions", period
        )  # Line 7
        # Line 8 - All Motana subtractions reduced by tier 1 railroad retirement benefits
        # and subtraction from federal taxable social security benefits
        # this is currently not included in the model, so we process with the
        # total value of mt_other_subtractionss
        subtractions = tax_unit("mt_other_subtractions", period)  # line 8
        subtracts = above_the_line_deductions + subtractions
        return adds - subtracts
