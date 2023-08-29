from policyengine_us.model_api import *


class mt_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana base exemption for head and spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        return p.amount * tax_unit("head_spouse_count", period)
