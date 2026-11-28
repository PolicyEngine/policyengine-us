from policyengine_us.model_api import *


class ri_property_tax_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Rhode Island total household income for the property tax credit computation"
    )
    documentation = (
        "Household income for the Rhode Island property tax credit "
        "(RI-1040H line 32): ri_property_tax_income of every tax unit in the "
        "household, so members who file their own returns count. Each tax "
        "unit in the household gets the same total."
    )
    reference = (
        # R.I. Gen. Laws 44-33-3(5), (6).
        "http://webserver.rilegislature.gov/Statutes/TITLE44/44-33/44-33-3.htm",
        # PDF pages 2-3: Part 5 and the definition of household income.
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2026-01/2025%201040H_w.pdf#page=2",
    )
    defined_for = StateCode.RI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # R.I. Gen. Laws 44-33-3(6): "all income received by all persons of a
        # household"; (5): a household is "one or more persons occupying a
        # dwelling unit and living as a single nonprofit housekeeping unit".
        # Each tax unit's income is counted once, through its head, and the
        # household total goes back to every tax unit through its members.
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        unit_income = person.tax_unit("ri_property_tax_income", period)
        household_income = person.household.sum(unit_income * head)
        return tax_unit.sum(household_income * head)
