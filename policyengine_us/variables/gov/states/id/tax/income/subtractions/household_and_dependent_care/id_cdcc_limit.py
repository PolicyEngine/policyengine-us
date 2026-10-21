from policyengine_us.model_api import *


class id_cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal CDCC-relevant care expense limit for Idaho tax purposes"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/governance/statutes/irc/",
        "https://tax.idaho.gov/taxes/income-tax/individual-income/instruction-2021/",
        "https://legislature.idaho.gov/wp-content/uploads/sessioninfo/2022/legislation/H0472.pdf#page=1",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # H.B. 472 (2022) conformed Idaho to the IRC as in effect on January
        # 1, 2022, and the Tax Commission's instruction changes for 2021
        # returns set Form 39R Line 6 worksheet line 2 to $8,000 / $16,000,
        # so 2021 uses the ARPA limit.
        p = parameters(period).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit("capped_count_cdcc_eligible", period)
        # This is the raw federal per-qualifying-individual dollar limit. The
        # IRC § 129 employer-benefit reduction (Form 39R Line 6 worksheet line 4)
        # is applied against the operative Idaho cap in
        # id_household_and_dependent_care_expense_deduction, so it is not
        # subtracted here.
        return p.max * capped_count_cdcc_eligible
