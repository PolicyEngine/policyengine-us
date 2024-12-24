from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tax_unit_medicaid_income_level(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid/CHIP-related modified adjusted gross income (MAGI) level"
    unit = "/1"
    documentation = (
        "Medicaid/CHIP-related MAGI as fraction of federal poverty line."
        "Documentation: 'Federal poverty level (FPL)' at the following URL:"
        "URL: https://www.healthcare.gov/glossary/federal-poverty-level-fpl/"
        "**Pregnant Women:**"
        "  * Pregnant women are counted as themselves plus the number of children they are expecting to deliver"
        "    when determining household size for Medicaid eligibility."
        "  * Sources:"
        "      URL: https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11618&fileName=10%20CCR%25202505-10%208.100"
        "      URL: https://www.cms.gov/marketplace/technical-assistance-resources/special-populations-pregnant-women.pdf"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("medicaid_magi", period)

        pregnant_count = add(tax_unit, period, ["current_pregnancies"])
        tax_unit_size = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)

        medicaid_fpg = fpg(
            pregnant_count + tax_unit_size, state_group, period, parameters
        )

        return income / medicaid_fpg
