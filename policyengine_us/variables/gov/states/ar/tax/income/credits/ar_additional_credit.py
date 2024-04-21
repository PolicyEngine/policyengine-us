from policyengine_us.model_api import *

class ar_additional_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas additional credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameter):
        taxable_income = add(tax_unit, period, ["ar_taxable_income_indiv"])
        p = parameter(
            period
        ).gov.states.ar.tax.income.credits.additional
        amount = p.amount
