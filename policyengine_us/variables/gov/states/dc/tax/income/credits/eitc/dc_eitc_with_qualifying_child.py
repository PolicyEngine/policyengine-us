from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
)


class dc_eitc_with_qualifying_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC with qualifying children"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04",  # (f)
    )
    defined_for = "dc_eitc_has_qualifying_child"

    def formula(tax_unit, period, parameters):
        # D.C. Code 47-1806.04(f)(1)(B)-(B-2) match the federal credit
        # allowed under IRC 32. Before 2023 that is the federal credit itself,
        # which leaves out a qualifying child without a Social Security
        # number (IRC 32(c)(3)(D)) and denies ITIN filers (IRC 32(c)(1)(E)).
        federal_eitc = tax_unit("eitc", period)
        # From 2023, (f)(1)(D)(ii) computes the credit as if an ITIN met the
        # IRC 32(m) Social Security number rule for the filer, spouse and
        # qualifying children.
        person = tax_unit.members
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        child_count = tax_unit.sum(person("is_eitc_qualifying_child", period) & has_tin)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        itin_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            child_count > 0,
            filer_has_tin,
        )
        p = parameters(period).gov.states.dc.tax.income.credits.eitc
        federal_like_eitc = where(p.itin_eligible, itin_eitc, federal_eitc)
        return federal_like_eitc * p.with_children.match
