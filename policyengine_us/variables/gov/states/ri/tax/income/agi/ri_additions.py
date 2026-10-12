from policyengine_us.model_api import *


class ri_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island AGI Additions"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf#page=2"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.agi.additions
        # The additions modify the filers' federal AGI. A tax unit
        # dependent's income, including their federally excluded
        # unemployment compensation, is on their own return, so person-level
        # additions count only the head and spouse.
        return tax_unit_non_dep_add(tax_unit, period, p.additions)
