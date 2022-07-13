from openfisca_us.model_api import *


class md_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.exemptions.aged
        aged_head = (tax_unit("age_head", period) >= p.age).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= p.age).astype(int)
        return aged_head * p.amount + aged_spouse * p.amount
