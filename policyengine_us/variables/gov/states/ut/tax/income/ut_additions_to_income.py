from policyengine_us.model_api import *


class ut_additions_to_income(Variable):
    """
    Line 5 on Utah 2022 Individual Income Tax return form TC-40. These
    additions to income include the following categories and are listed at
    https://incometax.utah.gov/additions with their accompanying codes.
    * 51: Lump sum distribution
    * 53: Medical care savings account (MSA) addback
    * 54: my529 addback
    * 56: Child's income excluded from parent's return
    * 57: Municipal bond interest
    * 60: Untaxed income of a resident trust
    * 61: Untaxed income of a nonresident trust
    * 67: Tax paid on behalf of a pass-through entity taxpayer
    * 68: Payroll Protection Program grant or loan addback
    * 69: Equitable adjustments
    """

    value_type = float
    entity = TaxUnit
    label = "UT additions to income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
