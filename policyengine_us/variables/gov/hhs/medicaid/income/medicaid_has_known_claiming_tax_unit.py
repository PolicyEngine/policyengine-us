from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._claiming_tax_unit import (
    NO_MEDICAID_CLAIMING_TAX_UNIT_ID,
)


class medicaid_has_known_claiming_tax_unit(Variable):
    value_type = bool
    entity = Person
    label = "Has a known claiming tax unit for Medicaid MAGI household rules"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"

    def formula(person, period, parameters):
        claiming_tax_unit_id = person("medicaid_claiming_tax_unit_id", period)
        tax_unit_id = person.tax_unit("tax_unit_id", period)
        return (claiming_tax_unit_id > NO_MEDICAID_CLAIMING_TAX_UNIT_ID) & np.isin(
            claiming_tax_unit_id, tax_unit_id
        )
