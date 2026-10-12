from policyengine_us.model_api import *


class ca_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "California taxable wages for earned income credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052",  # (c)(4)
        "https://www.ftb.ca.gov/forms/2025/2025-3514-booklet.html",  # Lines 13 and 23a
        "https://edd.ca.gov/siteassets/files/pdf_pub_ctr/de231eb.pdf#page=3",  # HSA payroll contributions
    )

    def formula(person, period, parameters):
        # FTB 3514 line 13 uses California wages (W-2 box 16), which also
        # enter the YCTC wage ceiling on line 23a. Traditional elective
        # deferrals and pre-tax health premiums are excluded, but payroll
        # HSA contributions remain California-taxable wages. Floor state
        # wages once, before netting business income or losses.
        excluded_wages = add(
            person,
            period,
            [
                "traditional_401k_contributions",
                "traditional_403b_contributions",
                "pre_tax_health_insurance_premiums",
            ],
        )
        return max_(0, person("employment_income", period) - excluded_wages)
