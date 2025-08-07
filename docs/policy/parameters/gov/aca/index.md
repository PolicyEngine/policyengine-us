# GOV › ACA Parameters

This section contains 26 parameters.

## Categories

- [AGE_CURVES](age_curves/index.md) (10 parameters)
- [ENROLLMENT](enrollment/index.md) (1 parameters)
- [FAMILY_TIER_RATINGS](family_tier_ratings/index.md) (2 parameters)
- [SLCSP](slcsp/index.md) (4 parameters)
- [SPENDING](spending/index.md) (1 parameters)

## Parameters

### `family_tier_states`
*Family tier rating states*

States that use family tier rating rather than summing individual age-rated premiums

**Unit: bool | Period: year**


### `ineligible_immigration_statuses`
*Reconciliation Premium Tax Credit immigration status adjustment in effect*

Ineligible immigration status for Premium Tax Credit.

**Unit: list | Period: year**

Current value (2027-01-01): **[6 items]**


### `la_county_rating_area`
*Los Angeles County ACA rating areas by three-digit ZIP code*

Los Angeles County assigns three-digit ZIP codes to these Affordable Care Act rating areas.

**Period: year**


### `max_child_count`
*ACA maximum child count*

Maximum number of children who pay an age-based ACA plan premium.

**Period: year**

Current value (2014-01-01): **3**


### `ptc_income_eligibility`
*ACA PTC income eligibility conditions*

Eligibility for ACA Premium Tax Credit by percent of modified AGI to federal poverty line.

**Type: single_amount | Period: year**


### `ptc_phase_out_rate`
*Rate of ACA PTC phase out*

Rate of ACA PTC phase out by ACA MAGI percent of FPL.

**Type: single_amount**


### `state_rating_area_cost`
*Second Lowest Cost Silver Plan premiums by rating area*

Second Lowest Cost Silver Plan (SLCSP) premiums by rating area, normalized to age 0 .

**Unit: currency-USD | Period: month**


### `takeup_rate`
*ACA takeup rate*

Percentage of eligible people who do enroll in Affordable Care Act coverage, if eligible.

**Unit: /1 | Period: year**

Current value (2018-01-01): **0.672**

