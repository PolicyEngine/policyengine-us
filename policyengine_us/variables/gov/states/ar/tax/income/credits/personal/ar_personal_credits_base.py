from policyengine_us.model_api import *


class ar_personal_credits_base(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas base personal credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Only head and spouse are eligible for the personal credit amounts
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.ar.tax.income.credits.personal
        aged = person("age", period) >= p.age_threshold
        # Arkansas provides an additional "aged special" credit for people who
        # do not receive retirement or disability benefit exemptions.
        receives_retirement_or_disability_exemption = (
            person(
                "ar_retirement_or_disability_benefits_exemption_person", period
            )
            > 0
        )
        aged_special = aged & ~receives_retirement_or_disability_exemption
        # Blind filers get an additional personal tax credit amount
        blind = person("is_blind", period)
        # Deaf filers get an additional personal tax credit amount
        deaf = person("is_deaf", period)
        # Widowed and head of household filers receive an additional credit amount
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        widow = filing_status == statuses.WIDOW
        hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
        filing_status_eligible = widow | hoh

        personal_credit_count = tax_unit.sum(
            head_or_spouse
            * (
                1
                + aged.astype(int)
                + blind.astype(int)
                + deaf.astype(int)
                + aged_special.astype(int)
            )
        ) + filing_status_eligible.astype(int)
        return personal_credit_count * p.amount.base
