"""Inputs for the exclusion of gain on the sale of a main home (IRC 121).
Enter them on the seller (for a jointly owned home on a joint return, on
the head). The gain must not also be reported in capital gains inputs."""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/121",
    "https://www.irs.gov/publications/p523",
)


def _input(name, value_type, label, documentation, unit=None):
    attributes = dict(
        value_type=value_type,
        entity=Person,
        definition_period=YEAR,
        label=label,
        documentation=documentation,
        reference=_REF,
        __module__=__name__,
    )
    if unit:
        attributes["unit"] = unit
    globals()[name] = type(name, (Variable,), attributes)


_input(
    "home_sale_gain",
    float,
    "Gain on the sale of a main home",
    "Amount realized less adjusted basis, before the section 121 exclusion. A loss is not deductible; enter 0.",
    USD,
)
_input(
    "home_sale_ownership_months",
    int,
    "Months the seller owned the home in the 5 years before the sale",
    "Months of ownership in the 60 months ending on the sale date.",
)
_input(
    "home_sale_use_months",
    int,
    "Months the seller used the home as a main home in the 5 years before the sale",
    "Months of use as a main home in the 60 months ending on the sale date.",
)
_input(
    "home_sale_spouse_meets_use_test",
    bool,
    "Spouse also used the home as a main home for 24 months",
    "On a joint return, whether the spouse meets the use test (needed for the joint amount).",
)
_input(
    "home_sale_excluded_gain_within_two_years",
    bool,
    "Seller excluded gain on another home in the prior 2 years",
    "IRC 121(b)(3): bars the exclusion unless a reduced exclusion applies.",
)
_input(
    "home_sale_spouse_excluded_gain_within_two_years",
    bool,
    "Spouse excluded gain on another home in the prior 2 years",
    "On a joint return, bars the joint amount.",
)
_input(
    "home_sale_reduced_exclusion_qualifies",
    bool,
    "Sale due to a change of employment, health or unforeseen circumstances",
    "IRC 121(c): a seller failing the 24-month or 2-year tests gets a fraction of the exclusion.",
)
_input(
    "home_sale_months_since_prior_exclusion",
    int,
    "Months since the last sale with an excluded gain",
    "Used for the reduced exclusion; leave 0 if there was no prior exclusion in the last 2 years.",
)
_input(
    "home_sale_nonqualified_use_share",
    float,
    "Share of the gain allocated to nonqualified use",
    "IRC 121(b)(5): periods after 2008 the home was not the main home (before it became one), over total ownership.",
    "/1",
)
_input(
    "home_sale_depreciation_after_may_6_1997",
    float,
    "Depreciation claimed on the home after May 6, 1997",
    "IRC 121(d)(6): gain up to this depreciation is not excluded. Also report it in unrecaptured_section_1250_gain_before_losses.",
    USD,
)
