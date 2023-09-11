from policyengine_us.model_api import *


class ar_personal_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas personal credit"
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
        us_aged = person("age", period)
        p = parameters(period).gov.states.ar.tax.income.credits.personal
        aged_thres = p.age_threshold
        p_ar = p.amount
        aged_count = tax_unit.sum(us_aged >= aged_thres)
        aged_credit = aged_count * p_ar.aged

        person = tax_unit.members
        us_blind = person("is_blind", period)
        total_blind = tax_unit.sum(us_blind)
        blind_credit = total_blind * p_ar.blind

        person = tax_unit.members
        us_deaf = person("is_deaf", period)
        total_deaf = tax_unit.sum(us_deaf)
        deaf_credit = total_deaf * p_ar.deaf

        us_dependent = tax_unit("tax_unit_dependents", period)
        dependent_credit = us_dependent * p_ar.dependent
        return aged_credit + blind_credit + deaf_credit + dependent_credit
