from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia senior citizen or disability deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible_person = person(
            "wv_senior_citizen_disability_deduction_eligible_person", period
        )
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction
        modification_amount = person("wv_total_modification", period)
        reduced_deduction_amount = max_(0, p.cap - modification_amount)
        total_reduced_amount = eligible_person * reduced_deduction_amount

        return tax_unit.sum(total_reduced_amount)
