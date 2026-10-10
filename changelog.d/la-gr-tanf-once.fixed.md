Count the SPM unit's CalWORKs (tanf) once in Los Angeles County General Relief gross income instead of once per member.

The public `la_general_relief_gross_income` variable moves from Person to SPMUnit. Callers supplying it must move the input from `people` to `spm_units`; direct calculations now return one value per SPM unit instead of one per person.

Break the circular housing subsidy and rent contribution calculation reached when corrected income permits housing assistance. Separate the county subsidy amount from the total landlord payment so supplied rent contributions affect both the housing payment and cash grant deduction, preserving main's contribution-override behavior.

The existing `la_general_relief_housing_subsidy` remains the total landlord payment. Callers supplying a county subsidy to determine the rent contribution must now supply `la_general_relief_housing_subsidy_amount` instead; a supplied total payment no longer determines the contribution.
