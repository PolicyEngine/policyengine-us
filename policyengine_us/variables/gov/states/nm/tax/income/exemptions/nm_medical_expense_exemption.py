from policyengine_us.model_api import *


class nm_medical_expense_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense exemption"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503680/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsADh4BKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.nm.tax.income.exemptions.unreimbursed_medical_expense
        age = person("age", period)
        medical_exepenses = tax_unit("medical_out_of_pocket_expenses", period)
        age_eligible = tax_unit.any(age >= p.age_eligibility)
        expense_eligible = medical_exepenses >= p.min_expenses
        eligible = age_eligible & expense_eligible
        return eligible * p.amount
