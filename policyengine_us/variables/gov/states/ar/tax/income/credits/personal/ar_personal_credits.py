from policyengine_us.model_api import *


class ar_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas personal credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    # The formula is modeled after the Tax Form AR1000F as opposed to the legal code
    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Only head and spouse are eligible for the personal credit amounts
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        total_head_or_spouse = tax_unit.sum(head_or_spouse)
        age = person("age", period) * head_or_spouse
        p = parameters(period).gov.states.ar.tax.income.credits.personal
        age_eligible = age >= p.age_threshold
        # Filers have to be over a certain age threshold to get
        # the aged personal credit
        total_age_eligible = tax_unit.sum(age_eligible)
        # An additiuonal aged credit is available for people who are not
        # receiving retirement or disability benefit exemption amounts
        disability_exemption_eligible = (
            person(
                "ar_retirement_or_disability_benefits_exemptions_indv", period
            )
            == 0
        )
        aged_special = age_eligible & disability_exemption_eligible
        total_aged_special = tax_unit.sum(aged_special)
        # Blind filers get an additional personal tax credit amount
        blind = person("is_blind", period) * head_or_spouse
        total_blind = tax_unit.sum(blind)
        # Deaf filers get an additional personal tax credit amount
        deaf = person("is_deaf", period) * head_or_spouse
        total_deaf = tax_unit.sum(deaf)
        # Widowed and heqad of household filer can receive an additional credit amount
        filing_status = tax_unit("filing_status", period)
        widow = filing_status == filing_status.possible_values.WIDOW
        head_of_household = (
            filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD
        )
        filing_status_eligible = widow | head_of_household
        dependent_credit = tax_unit(
            "ar_personal_credit_dependent_amount", period
        )
        personal_credit = (
            total_head_or_spouse
            + total_age_eligible
            + total_aged_special
            + total_blind
            + total_deaf
            + filing_status_eligible
        ) * p.amount.base
        return personal_credit + dependent_credit
