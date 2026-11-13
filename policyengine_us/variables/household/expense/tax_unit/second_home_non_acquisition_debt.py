from policyengine_us.model_api import *


class second_home_non_acquisition_debt(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second home non-acquisition debt"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Average balance of debt secured by the second home that is not home "
        "acquisition debt (not used to buy, build or substantially improve "
        "it). The pre-TCJA mortgage interest limits, which New York keeps, "
        "treat it as home equity debt, up to $100,000 ($50,000 married filing "
        "separately) across both homes. On this home, that debt also can't "
        "exceed the home's value (second_residence_value) less the part of "
        "second_home_mortgage_balance treated as acquisition debt. Publication "
        "936 (2017) measures that value and debt on the date the last debt was "
        "secured by the home; PolicyEngine approximates both with current "
        "values. Include the interest on this debt in "
        "second_residence_mortgage_interest. PolicyEngine's federal "
        "calculation reads only the acquisition mortgage balances, so after "
        "2017 it treats that interest like interest on those balances: fully "
        "deductible when they fit the federal limit, and deductible at the "
        "same share when they don't. Defaults to 0, which leaves the pre-TCJA "
        "calculation to the acquisition mortgage balances."
    )
    reference = (
        # 26 U.S.C. 163(h)(3)(C), 2016 edition.
        "https://www.govinfo.gov/content/pkg/USCODE-2016-title26/html/USCODE-2016-title26-subtitleA-chap1-subchapB-partVI-sec163.htm",
        # PDF pages 10, 13
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=10",
    )
