from policyengine_us.model_api import *


class va_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Married couple files separately on VA tax return"
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/filing-status",
        "https://law.lis.virginia.gov/vacode/58.1-322.03/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18",
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        itax_indiv = person("va_itemized_deductions_indiv", period)
        itax_joint = person("va_itemized_deductions_joint", period)
        return itax_indiv < itax_joint
