from policyengine_us.model_api import *


class ar_aged_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas aged personal credit"
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
        aged_thres = parameters(
            period
        ).gov.states.ar.tax.income.credits.personal.aged_threshold

        p_ar = parameters(
            period
        ).gov.states.ar.tax.income.credits.personal.amount

        aged_count = 0
        if us_aged >= aged_thres:
            aged_count = aged_count + 1
        return aged_count * p_ar.aged
