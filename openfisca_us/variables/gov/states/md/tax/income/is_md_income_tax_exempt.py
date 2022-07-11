from openfisca_us.model_api import *
from openfisca_us.variables.gov.states.md.tax.income.exemption.md_total_personal_exemptions import (
    md_total_personal_exemptions,
)


class is_md_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "MD income tax exempt"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):

        agi = tax_unit("adjusted_gross_income", period)
        # Check if agi less than md_total_personal_exemptions
        md_total_personal_exemptions = tax_unit(
            "md_total_personal_exemptions", period
        )
        return agi <= md_total_personal_exemptions
