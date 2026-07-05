from policyengine_us.model_api import *


class md_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Maryland withheld income tax"
    defined_for = StateCode.MD
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        p = parameters(period).gov.states.md.tax.income
        # We apply the maximum standard deduction amount
        standard_deduction = p.deductions.standard.max["SINGLE"]
        reduced_agi = max_(agi - standard_deduction, 0)
        state_withheld = p.rates.single.calc(reduced_agi)
        # Maryland employers withhold county income tax together with the
        # state tax (Form 502 line 41 reports combined Maryland and local
        # withholding), so the estimate includes the county component.
        county = person.household("county_str", period)
        # Guard against non-MD counties in microsimulation:
        # defined_for masks results but doesn't prevent formula execution.
        in_md = person.household("state_code_str", period) == "MD"
        safe_county = where(in_md, county, "ALLEGANY_COUNTY_MD")
        p_local = parameters(period).gov.local.md
        flat_rate_withheld = p_local.flat_rate[safe_county] * reduced_agi
        is_anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"
        anne_arundel_withheld = p_local.anne_arundel_county.tax.income.single.calc(
            reduced_agi
        )
        is_frederick = county == "FREDERICK_COUNTY_MD"
        frederick_withheld = (
            p_local.frederick_county.tax.income.single.calc(reduced_agi, right=True)
            * reduced_agi
        )
        local_withheld = select(
            [is_anne_arundel, is_frederick],
            [anne_arundel_withheld, frederick_withheld],
            default=flat_rate_withheld,
        )
        return state_withheld + local_withheld * in_md
