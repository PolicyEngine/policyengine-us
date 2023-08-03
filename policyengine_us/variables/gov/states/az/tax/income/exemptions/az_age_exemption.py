from policyengine_us.model_api import *


class az_age_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona age exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        p = parameters(period).gov.states.az.tax.income.exemptions

        age_head = tax_unit("age_head", period)
        head_eligible = (age_head >= p.min_age).astype(int)
        dependent_head = tax_unit("dsi", period).astype(int)

        age_spouse = tax_unit("age_spouse", period)
        spouse_eligible = (age_spouse >= p.min_age).astype(int)
        dependent_spouse = tax_unit("dsi_spouse", period).astype(int)

        return (head_eligible * ~dependent_head + spouse_eligible * ~dependent_spouse * joint) * p.amount.age
