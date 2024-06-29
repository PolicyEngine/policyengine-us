from policyengine_us.model_api import *


class ar_taxable_income_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable income for each individual"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, parameters, period):
        filing_separately = person.tax_unit("ar_files_separately", period)
        taxable_income_indiv = person("ar_taxable_income_indiv", period)
        taxable_income_joint = person("ar_taxable_income_joint", period)
        return where(
            filing_separately, taxable_income_indiv, taxable_income_joint
        )
