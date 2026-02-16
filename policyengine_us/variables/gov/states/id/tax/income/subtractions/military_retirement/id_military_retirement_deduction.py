from policyengine_us.model_api import *


class id_military_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho military retirement deduction"
    unit = USD
    reference = (
        "https://legislature.idaho.gov/sessioninfo/2025/legislation/H0040/",
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
    )
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.subtractions.military_retirement
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        military_retirement_pay = person("military_retirement_pay", period)
        eligible_military_pay = military_retirement_pay * head_or_spouse
        # Multiply by applies parameter (False when military retirement
        # is already handled in general retirement benefits deduction)
        return tax_unit.sum(eligible_military_pay) * p.applies
