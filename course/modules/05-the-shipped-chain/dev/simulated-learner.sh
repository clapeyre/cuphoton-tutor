#!/bin/bash
# Simulated learner through Module 05 against the test server on :8799.
cd /home/clapeyre/AI_TUTOR_CUPHOTON
say() { # lesson turn text
  echo "=== $1/$2: ${3:0:80}" ; PORT=8799 WAIT=900000 npx tsx tools/ws-drive.ts "$(python3 -c 'import json,sys; print(json.dumps({"type":"say","lesson":sys.argv[1],"turn":sys.argv[2],"text":sys.argv[3]}))' "$1" "$2" "$3")" > /dev/null 2>&1; echo "  -> exit $?"
}
open_() { echo "=== open $1"; PORT=8799 WAIT=600000 npx tsx tools/ws-drive.ts "{\"type\":\"open\",\"lesson\":\"$1\"}" >/dev/null 2>&1; echo "  -> exit $?"; }
open_ 5.1
say 5.1 settings "Can you show me the survey block of the shipped configuration?"
say 5.1 settings "The variance kind must be variance, not inverse variance: the PS1 var files are variances. The reference needs its own variance and mask planes. Both nights are already on the same grid, so on_target_grid should be true. And the mask policy should be the 8575 bits from 4.1. Please write it and run it."
say 5.1 success "Let me see the supernova's row in the catalog, and the uq section of the summary."
say 5.1 success "The flux is NaN and the budget says no PSF width. It needs a PSF width; we used 1.57 px in 4.4. Set it and rerun."
open_ 5.2
say 5.2 same-answer "It finds the supernova at about the same flux as my 4.4 measurement. Stars A, B and D from 4.3 are there too, plus another star, but each appears in several rows: the positive and negative parts of the twisted residues. So 12 rows but only about six places."
say 5.2 trust-a-row "Which quality flags are set on that row, and which of its error columns are NaN?"
say 5.2 trust-a-row "The flux error is defined; only the centre isn't, because the dipole's second lobe went far off. So I can use the flux and its error bar."
open_ 5.3
say 5.3 budget "Show me the terms of the error bar."
say 5.3 budget "Most of it is the corr term: the correlated noise from 4.4, measured on this image. A factor 1.8 is a bit more than my 1.2 to 1.5 but within the range of the box test."
say 5.3 test-it "Plant fakes at 2000, 4000 and 8000 counts in the target only, with the target PSF, more than a stamp width apart, away from stars, masks and the supernova, ten images with ten per level. Measure the fraction found, measured over planted, and pulls against the chain's error bar. Run it."
say 5.3 what-went-wrong "The pulls have about the right width but are centred around minus 1.2, and the fluxes come back 5 to 10 percent low. Something biases them. Can I see the kernel fit numbers in the summary?"
say 5.3 what-went-wrong "A chi2 per degree of freedom of 16 on under 5000 pixels is a bad kernel fit. Fit the kernel on the whole image and rerun the test."
open_ 5.4
say 5.4 rules "For every image I'd record the kernel chi2/dof and how many pixels it used, where the PSF width came from and which error terms were left out, which reader ran and any fallback, and the candidate count. Flag chi2/dof above 3, and flag any error term left out for lack of a PSF width. Build it and show me."
say 5.4 module-question "Not by default: it finished and said success while it left out the fluxes and then biased them. You find out by reading what it wrote and testing it with planted sources."
echo DONE
