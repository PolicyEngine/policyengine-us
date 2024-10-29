from policyengine_us.model_api import *


class in_base_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana base exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(3)-(4)
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.exemptions
        # Personal exemptions
        non_dependent_exemptions = p.base.amount
        # Dependent exemptions
        dependents = tax_unit("tax_unit_dependents", period)
        unit_size = tax_unit("tax_unit_size", period)
        unit_without_dependents = max_(unit_size - dependents, 0)
        total_base = unit_without_dependents * non_dependent_exemptions
        # Total the number of dependents
        dependent_exemptions = dependents * p.base.dependent
        # total exemptions
        return total_base + dependent_exemptions
