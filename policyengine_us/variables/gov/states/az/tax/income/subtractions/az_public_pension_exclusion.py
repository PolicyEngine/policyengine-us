from policyengine_us.model_api import *


class az_public_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Pension Exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=18",
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=23",
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2011_itr11-3.pdf#page=2",
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.subtractions.pension
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Arizona counts SBP annuities as benefits from a plan established by
        # federal law (43-1022(2); ITR 11-3). From 2023, a surviving spouse
        # reports these payments on line 29b instead.
        p_military = parameters(
            period
        ).gov.states.az.tax.income.subtractions.military_retirement
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        on_line_29b = surviving_spouse & p_military.surviving_spouse_eligible
        pension_income = person("taxable_public_pension_income", period) + where(
            on_line_29b, 0, survivor_pay
        )
        eligible_pension_income = pension_income * head_or_spouse
        total_allowed_pension_exclusion = min_(
            p.public_pension_cap, eligible_pension_income
        )
        return tax_unit.sum(total_allowed_pension_exclusion)
