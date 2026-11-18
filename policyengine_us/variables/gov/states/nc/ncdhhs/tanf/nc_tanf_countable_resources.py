from policyengine_us.model_api import *


class nc_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable resources"
    unit = USD
    definition_period = YEAR
    quantity_type = STOCK
    reference = (
        "https://regulations.justia.com/states/north-carolina/title-10a/chapter-71/subchapter-w/section-0400/section-71w-0407",
        # PDF pages 6-7
        "http://reports.oah.state.nc.us/ncac/title%2010a%20-%20health%20and%20human%20services/chapter%2071%20-%20adult%20and%20family%20support/subchapter%20w/subchapter%20w%20rules.pdf#page=6",
        # PDF pages 2-4
        "https://policies.ncdhhs.gov/wp-content/uploads/wf115.pdf#page=2",
    )
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # 10A NCAC 71W .0407(d)-(e) and Work First Manual section 115, II:
        # cash, checking and savings accounts, stocks, bonds and mutual fund
        # shares count; motor vehicles, real property and retirement funds do
        # not. Simplification: .0407(d)(3) and (e)(5) exclude the part of a
        # checking account that is the month's income deposited for the
        # family's needs, but bank_account_assets has no such split, so the
        # full balance counts.
        total = spm_unit("spm_unit_cash_assets", period)
        # .0407(b)(1)-(2): a parent's resources count unless the parent
        # receives SSI, and a child's count only if the child is in the
        # payment, which SSI recipients are not (as in nc_tanf_household_size
        # and the NC TANF income variables). The excluded members' share is
        # subtracted from the unit aggregate, so households that supply only
        # spm_unit_cash_assets keep the aggregate behavior.
        # Limitation: .0407(b) does not list non-parent adults (for example a
        # grandparent caretaker in a child-only case, an adult sibling or an
        # unmarried partner), but their resources count here, as their income
        # does in the NC TANF income variables.
        person = spm_unit.members
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # Read the components from spm_unit_cash_assets.adds, so the
        # subtraction removes exactly the excluded members' share.
        components = spm_unit.simulation.tax_benefit_system.get_variable(
            "spm_unit_cash_assets"
        ).adds
        person_assets = add(person, period, components)
        excluded_assets = spm_unit.sum(person_assets * is_ssi_recipient)
        return max_(total - excluded_assets, 0)
