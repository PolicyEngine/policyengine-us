from policyengine_us.model_api import *


class ca_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "California spouse's adjusted earnings"
    documentation = (
        "Spouse's earned income subject to California tax "
        "(ca_adjusted_earnings), which counts the payroll HSA contributions "
        "that federal W-2 box 1 wages leave out."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.6",  # (d)(2)
        "https://www.ftb.ca.gov/forms/2025/2025-3506-instructions.html",  # Line 4
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        ca_adjusted_earnings = person("ca_adjusted_earnings", period)
        is_spouse = person("is_tax_unit_spouse", period)
        return tax_unit.sum(is_spouse * ca_adjusted_earnings)
