Extend `tip_income_deduction_occupation_requirement_met` to recognize
SSTB status from the per-category `sstb_self_employment_income` input,
not only the legacy all-or-nothing `business_is_sstb` flag. This keeps
the §224 SSTB exclusion in force for self-employed tipped workers who
populate the new SSTB inputs added in #7944.
