from policyengine_us.model_api import *


class nm_medical_expense_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Mexico unreimbursed medical expense credit"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503776/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDswgGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.nm.tax.income.credits.unreimbursed_medical_expense
        age = person("age", period)
        medical_exepenses = tax_unit("medical_out_of_pocket_expenses", period)
        