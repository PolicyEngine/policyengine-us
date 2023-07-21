from policyengine_us.model_api import *


class nm_hundred_year_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico hundred year exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503677/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsAdlEBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        p = parameters(period).gov.states.nm.tax.income.exemptions.hundred_year
        eligible = (age_head | age_spouse) >= p.age_eligibility
        total_income = tax_unit("nm_taxable_income", period)
        # If the head or spouse are over 100, then they get a full exemption
        return eligible * total_income
