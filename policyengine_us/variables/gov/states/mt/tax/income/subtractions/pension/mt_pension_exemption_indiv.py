from policyengine_us.model_api import *


class mt_pension_exemption_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana partial pension, annuity, and IRA income exemption on a separate return"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=6",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=34",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.pension.phase_out
        exemption = person("mt_pension_exemption_before_phase_out", period)
        # Lines 4-6: a single filer, or each spouse filing separately, reduces
        # the exemption by their own federal adjusted gross income. Spouses
        # filing separately on the same form divide the return's losses
        # equally, as in mt_agi_indiv.
        agi = person("adjusted_gross_income_person", period) + person(
            "mt_loss_ald_reallocation", period
        )
        reduction = p.rate * max_(agi - p.threshold, 0)
        # Line 7
        return max_(exemption - reduction, 0)
