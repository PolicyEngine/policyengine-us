from policyengine_us.model_api import *


class ca_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "California spouse's adjusted earnings"
    documentation = (
        "Spouse's earned income subject to California tax: spouse_earned plus "
        "the payroll HSA contributions that California taxes but federal "
        "W-2 box 1 wages leave out."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.6",  # (d)(2)
        "https://www.ftb.ca.gov/forms/2025/2025-3506-instructions.html",  # Line 4
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",  # Line 1h
        "https://www.ftb.ca.gov/forms/2025/2025-1005-publication.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        # R&TC 17052.6(d)(2) limits earned income to "earned income subject
        # to tax under this part", and FTB 3506 line 4 counts "other taxable
        # employee compensation". California does not exclude payroll HSA
        # contributions (Schedule CA (540) line 1h, column C), so its wages
        # (ca_taxable_wages, W-2 box 16) exceed federal taxable wages by them.
        person = tax_unit.members
        ca_only_wages = max_(
            0,
            person("ca_taxable_wages", period)
            - person("irs_employment_income", period),
        )
        return tax_unit("spouse_earned", period) + tax_unit.sum(
            ca_only_wages * person("is_tax_unit_spouse", period)
        )
