from policyengine_us.model_api import *


class mt_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Montana LIHEAP eligibility"
    defined_for = StateCode.MT
    reference = (
        # PDF pages 1-2
        "https://rules.mt.gov/policy-library-documents/application/pdf/5475239b875d29ebe7cf1f12b38458830f87a4a18c8dd600b7548603204fccd9#page=1",
        # PDF pages 1-2
        "https://rules.mt.gov/policy-library-documents/application/pdf/5389d31b170322ad8de7c67ca74832a2fe762425962ec410fe9a737193afe951#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/b2d910910cc1ecf830fc66d844708df2504ed257f556ce252cc3b4d25dc84a88#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/f314cbda8448e499b69120f0401d35836fe02c4884e961091b2d56c86e3b1abc#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/68a4c23444a94d952bc1fa28f5b3c8f528f075b616525c34295b11b0630e1e4f#page=1",
        # PDF pages 28-31, 126
        "https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=28",
        # PDF pages 9-10
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.eligibility
        size = spm_unit("mt_liheap_household_size", period)
        # Categorically eligible households need no income or resource test
        # (ARM 37.70.402(2)).
        categorical = spm_unit("mt_liheap_categorical_eligibility", period)
        is_categorical = categorical != categorical.possible_values.NONE
        income = spm_unit("mt_liheap_countable_income", period)
        income_eligible = income <= spm_unit("mt_liheap_income_limit", period)
        # ARM 37.70.408(1)-(2): cash, stocks, bonds and non-home real estate
        # count against the size-based limit; business equity has its own
        # limit (see business_equity_limit.yaml).
        non_business_resources = (
            spm_unit("spm_unit_cash_assets", period)
            + spm_unit.household("household_other_real_estate_equity", period)
            + spm_unit.household("household_rental_property_equity", period)
        )
        business_equity = spm_unit.household("household_business_assets_equity", period)
        non_business_eligible = non_business_resources <= p.resources.limit.calc(size)
        business_eligible = business_equity <= p.resources.business_equity_limit
        resource_eligible = non_business_eligible & business_eligible
        financially_eligible = is_categorical | (income_eligible & resource_eligible)
        # ARM 37.70.402(1): the household must be obligated to pay for heating
        # fuel, directly or through rent. An unreported fuel (UNSPECIFIED)
        # pays $0, as in the other state LIHEAP programs (issue 9754).
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        heating_reported = (heating_type != fuel.UNSPECIFIED) & (
            heating_type != fuel.NONE
        )
        has_heating_expense = spm_unit("has_heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        obligated = has_heating_expense | heat_in_rent
        # Not modeled: shelters and excluded group homes (ARM 37.70.402(4)),
        # students claimed by an outside taxpayer (402(5), repealed May 23,
        # 2026), households in the tribal LIHEAP service population (402(6),
        # numbered (5) from May 23, 2026), SSN or status refusal (402(9),
        # numbered (8) from May 23, 2026), credit balances (ARM
        # 37.70.607(1)(c)) and transfers of resources.
        return (size > 0) & financially_eligible & heating_reported & obligated
