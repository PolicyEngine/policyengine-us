from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.credits.cdcc.min_head_spouse_earned import (
    lesser_head_spouse_earned,
)


class ca_cdcc_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lesser of head and spouse's California CDCC earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.6",  # (d)(2)
        "https://www.ftb.ca.gov/forms/2025/2025-3506-instructions.html",  # Lines 4 and 5
    )

    def formula(tax_unit, period, parameters):
        # FTB 3506 lines 4 and 5 use California earned income (which counts
        # payroll HSA contributions) and deem a student or disabled spouse's
        # earnings at $250 ($500) a month, as federal Form 2441 does.
        return lesser_head_spouse_earned(
            tax_unit,
            period,
            parameters,
            tax_unit("ca_head_earned", period),
            tax_unit("ca_spouse_earned", period),
        )
