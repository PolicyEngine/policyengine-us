from policyengine_us.model_api import *


class mn_k12_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Minnesota K-12 qualifying children count"
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0674",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ed-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # A qualifying child must:
        # - Be in grades K-12
        # - Be a dependent
        # - Have lived with the filer more than half the year
        # Using is_in_k12_school and is_tax_unit_dependent as proxies
        is_k12 = tax_unit.members("is_in_k12_school", period)
        is_dependent = tax_unit.members("is_tax_unit_dependent", period)
        return tax_unit.sum(is_k12 & is_dependent)
