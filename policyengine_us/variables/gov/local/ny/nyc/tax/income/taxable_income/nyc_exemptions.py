from policyengine_us.model_api import *


class nyc_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCadmin/0-0-0-13966"
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        count_dependents = tax_unit("tax_unit_count_dependents", period)
        dependent_exemption = parameters(
            period
        ).gov.local.ny.nyc.tax.income.taxable_income.exemptions.dependent
        return dependent_exemption * count_dependents
