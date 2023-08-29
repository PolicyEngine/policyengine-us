from policyengine_us.model_api import *


class mt_aged_exemption_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of Montana aged exemptions"
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        aged_head = (tax_unit("age_head", period) >= p.age_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.age_threshold
        ).astype(int)
        return aged_head + aged_spouse
