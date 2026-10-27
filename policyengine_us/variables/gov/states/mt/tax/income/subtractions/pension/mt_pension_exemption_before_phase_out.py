from policyengine_us.model_api import *


class mt_pension_exemption_before_phase_out(Variable):
    value_type = float
    entity = Person
    label = "Montana partial pension, annuity, and IRA income exemption before the phase-out"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=6",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=34",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.pension
        if not p.in_effect:
            return 0
        # Worksheet lines 1-3a: the smaller of the cap and the taxpayer's own
        # pension, annuity, and IRA income.
        income = add(person, period, p.sources)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * min_(p.cap, income)
