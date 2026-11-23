from policyengine_us.model_api import *


class az_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona military retirement subtraction"
    unit = USD
    reference = (
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=25",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=27",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf",
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2011_itr11-3.pdf#page=2",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.subtractions.military_retirement
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # In ITR 11-3, ADOR puts SBP benefits under 43-1022(2)
        # (az_public_pension_exclusion). From 2023, ADOR moves a deceased
        # veteran's surviving spouse's payments to line 29b in its Form 140
        # instructions.
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        on_line_29b = surviving_spouse & p.surviving_spouse_eligible
        military_retirement_income = retirement_pay + survivor_pay * on_line_29b
        eligible_military_pay = military_retirement_income * head_or_spouse
        capped_military_pay = min_(eligible_military_pay, p.max_amount)
        return tax_unit.sum(capped_military_pay)
