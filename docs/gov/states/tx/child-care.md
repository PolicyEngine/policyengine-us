# Texas Child Care Services care hours

Texas Child Care Services (CCS) selects provider payment rates using
`tx_ccs_care_schedule`. Its formula derives the category from reported hours when
the schedule is not supplied:

1. An explicit `tx_ccs_care_schedule` of `FULL_TIME`, `PART_TIME`, or `BLENDED`
   takes precedence. This represents a known schedule or authorization, which
   occasional differences in attendance do not change.
2. Otherwise, positive `childcare_hours_per_day` determines the category.
3. When daily hours are unknown, positive `childcare_hours_per_week` divided by
   positive `childcare_days_per_week` supplies the average daily hours. Weekly
   hours alone do not establish the length of a care day.
4. If daily hours remain unknown, the model selects the full-time rate.

For reported hours, a positive day shorter than six hours selects `PART_TIME`;
six hours or more selects `FULL_TIME`. The six-hour threshold comes from
[40 TAC §809.93(e), effective January 8, 2013](https://www.twc.texas.gov/sites/default/files/ogc/docs/fr-809-ch-rev-12-12-twc.pdf#page=74).
The rule defines a full-day unit as six to twelve hours and preserves explicit
enrollment when attendance occasionally differs. The model selects one rate per
billable day; it does not infer additional units from unusually long days.
An explicit `BLENDED` schedule selects its own rate without another part-time
reduction. See also [TWC WD 02-20](https://www.twc.texas.gov/sites/default/files/ccel/docs/02-20-twc.pdf#page=3).

## Unknown hours and no care

The shared numeric hour inputs default to zero. Omitted hours and explicitly
supplied zero hours therefore both mean unknown intensity for this classification.
The full-time fallback is a modeling assumption, not evidence of enrollment or
observed full-time attendance. Population analyses should supply observed or
appropriately imputed hours or authorizations when available.

Payment still multiplies the daily rate by
`childcare_attending_days_per_month`. Zero billable days produce zero payment for
that child, regardless of the resolved category. A household with no care should
have zero billable days for its children and zero
`spm_unit_pre_subsidy_childcare_expenses`; its CCS benefit remains zero. Zero hours
alone do not cancel positive billable days or expenses. The existing eligibility,
expense cap, and copay formulas continue to apply. The modeled copay does not
vary with the full-time/part-time category.

## Batched schedule inputs

The existing `FULL_TIME`, `PART_TIME`, and `BLENDED` choices and `FULL_TIME`
default remain unchanged. The core input builder treats a supplied variable as
an array for the whole population. If any person supplies `tx_ccs_care_schedule`
for a month, omitted entries are filled with `FULL_TIME` and this formula is not
run for those entries. For example, a three-hour child without a supplied schedule
will receive the full-time rate when batched with another child whose schedule
is supplied explicitly.

This is a remaining core input limitation, not a Texas policy rule. When using
mixed explicit schedules in a batch, callers must supply each child's intended
schedule, or evaluate households separately without partially populated schedule
arrays. Mixed explicit and derived schedules remain unresolved under issue #9524;
this Texas formula change does not claim to fix that case.

This page describes the Texas implementation. Other state programs require
separate review of their thresholds, units, and authorization rules under
[issue #9524](https://github.com/PolicyEngine/policyengine-us/issues/9524).
