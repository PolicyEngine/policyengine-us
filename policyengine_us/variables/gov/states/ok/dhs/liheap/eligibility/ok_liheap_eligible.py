from policyengine_us.model_api import *


class ok_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Oklahoma LIHEAP regular heating assistance"
    defined_for = StateCode.OK
    # OAC 340:20-1-10(c)-(h), 340:20-1-11(a): eligible size, gross income
    # including deemed contributions, and responsibility for heating costs.
    reference = "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html"

    def formula(spm_unit, period, parameters):
        size = spm_unit("ok_liheap_household_size", period)
        income = spm_unit("ok_liheap_gross_income", period)
        income_limit = spm_unit("ok_liheap_income_limit", period)
        fuel = spm_unit("heating_type", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        expense = spm_unit("heating_expense", period)
        has_expense = spm_unit("has_heating_expense", period)
        subsidized = spm_unit.household("is_in_public_housing", period) | spm_unit(
            "receives_housing_assistance", period
        )
        # Housing flags proxy income-based rent. A positive heating expense
        # represents a verified surcharge when subsidized heat is in rent;
        # the general responsibility flag alone cannot satisfy that branch.
        rent_responsibility = ~subsidized | (expense > 0)
        # Direct expenses represent the remaining household obligation after
        # a utility allowance, rather than a fully reimbursed gross bill.
        direct_responsibility = has_expense | (expense > 0)
        responsibility = where(heat_in_rent, rent_responsibility, direct_responsibility)
        # Written roomer agreements, exact shared-meter/institutional facts,
        # and tribal LIHEAP receipt are not available as existing inputs.
        return (
            (size > 0)
            & (income <= income_limit)
            & (fuel != fuel.possible_values.NONE)
            & responsibility
        )
