from policyengine_us.model_api import *


class ca_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf",
        # 2020 Schedule CA (540) instructions, Part I, Section C, line 22,
        # column B: the federal Form 1040 line 10b charitable deduction.
        "https://www.ftb.ca.gov/forms/2020/2020-540-booklet.pdf#page=48",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Personal interest belongs on the member's own return. The existing
        # tax-unit additions already describe this return and remain intact.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "ca_hsa_addition",
                "ca_educator_expense_addition",
                "ca_other_additions",
                "charitable_contributions_ald",
                "ca_out_of_state_municipal_bond_interest",
                "ca_dependent_care_assistance_addition",
            ],
        )
