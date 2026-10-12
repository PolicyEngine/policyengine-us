Count the SPM unit's CalWORKs (tanf) once in Los Angeles County General Relief gross income instead of once per member.

The public `la_general_relief_gross_income` variable moves from Person to SPMUnit. Callers supplying it must move the input from `people` to `spm_units`; direct calculations now return one value per SPM unit instead of one per person.

Break the circular housing subsidy and rent contribution calculation reached when corrected income permits housing assistance. Separate the county allowance from the total landlord payment so supplied rent contributions affect both the housing payment and cash grant deduction, preserving main's contribution-override behavior for nonnegative contributions.

The existing `la_general_relief_housing_subsidy` remains the total landlord payment. The new `la_general_relief_housing_subsidy_amount` is the county allowance before the final landlord-payment cap. Callers supplying an allowance to determine the rent contribution must now supply that variable instead; a supplied total payment no longer determines the contribution.

Report additional county subsidy actually paid separately as `la_general_relief_housing_subsidy_paid`, equal to the landlord payment less the contribution, floored at zero. This prevents reporting the allowance as expenditure when the final rent cap reduces county aid, without changing existing payment or contribution formulas.
