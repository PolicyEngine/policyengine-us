from policyengine_us.model_api import *


class oasdi_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "OASDI modeled liabilities"
    documentation = (
        "Modeled OASDI liabilities: each member's oasdi_payroll_tax_revenue "
        "plus each tax unit's oasdi_benefit_taxation_revenue and "
        "oasdi_niit_revenue, each counted once. Excludes reserve interest, "
        "Railroad Retirement interchange and general-fund reimbursements, "
        "which the model does not represent. tob_revenue_oasdi differences "
        "income tax including the net investment income tax, so it carries "
        "the NIIT that benefit inclusion adds; with an S.770 section 8 option "
        "on, oasdi_niit_revenue's transfer also counts part of that increase."
    )
    unit = USD

    def formula(household, period, parameters):
        person = household.members
        payroll = household.sum(person("oasdi_payroll_tax_revenue", period))
        tax_unit = person.tax_unit
        tax_unit_revenue = tax_unit(
            "oasdi_benefit_taxation_revenue", period
        ) + tax_unit("oasdi_niit_revenue", period)
        # Credit each tax unit's amount once, to its first member's household,
        # whose weight the tax unit carries. Group-to-group adds would split
        # it by member count instead.
        first_member = tax_unit.reference_entity.members_position == 0
        return payroll + household.sum(where(first_member, tax_unit_revenue, 0))
