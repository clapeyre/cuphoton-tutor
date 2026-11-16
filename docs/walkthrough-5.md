# Walkthrough 5 · Module 04

Rough notes are fine. Put the lesson number first, and the time if you can.

## 4.1

## 4.2
Not easy to do all that from memory. We have all the classes on the side, so we can hop back, and that's good. Maybe a few hints to lessons one could jump back to, to see the most relevant parts of the answer, could be good. 

This is not the first time it's happened, but it's very obvious to me here. Sometimes it's very hard, given the width of the page, to see the plots that the agent made, and when I click on the image, nothing happens.

I think it would be really good to have a little image viewer where, when I click on an image, it goes full screen, maybe just as a hover on top of the rest. If I could zoom into it a little bit, or maybe just putting it full screen will be enough in a lot of cases. Right now, it's impossible to read sometimes. 
## 4.3

## 4.4
Did the last turn finish early? It was marked as finished, and when I looked at the conversation, it said "last steps for the module," and then it never asked me for anything there. 
## Overall
Interesting. Things are getting tougher here, but it's pushing me to have deep conversations with the tutors, so that's good. I like how there's not enough information, but you can just ask to plot new things. That's a dynamic that I think is really cool and is working pretty well here. Although I must say, I got a little bit confused by the variance explanations. I understand in principle that if your noise gets correlated, then it can get warped, but I didn't really understand the full logical sequence. I couldn't explain it back right now as to what happened and what would have needed to be different for it to work. 
## What changed in response

- **4.4, the last turn "finished early" (a bug, also latent in 1.7 and 3.4).** The tutor's notes said to ask the module question *after* settling the last turn, so it landed in a turn that had already closed its reply box. The module question is now a turn of its own: `module-question` in 1.7 and 3.4, and `next-night` ("Brief the next night") in 4.4. The tutor's rules now say never to ask anything in a reply that settles a turn. Your saved progress in 1.7, 3.4 and 4.4 shows the new turn open, if you want to answer it.
- **Plots too small to read.** Every image (lesson figures, the tutor's figures, turn images) now opens full screen on click. Click again or press +/− to zoom up to 400%, drag to move around, Esc or Close to go back.
- **Hints for where to hop back (4.2).** Lessons and tutor messages can link to earlier lessons (`[1.4](#/1.4)`). Browser Back returns you, and unsent text is kept. 4.2 now lists where each stage was built (1.3–1.6, 3.2, 4.1, 2.6), 4.1's prompts point to 1.1 and 1.2, and the tutor is told to link the lesson rather than re-teach it.
- **The correlated-noise explanation.** I measured it on the target's blank sky. The variance map is right pixel by pixel (scatter 0.9–1.07× its prediction). Each pixel's noise is about 20% shared with its direct neighbours, and nothing two pixels away. Summing blank sky over boxes, the real scatter exceeds the map's prediction by 1.08× (2×2), 1.29× (5×5), 1.60× (9×9) and 1.74× (11×11). The tutor's notes now give the argument in five steps, one per message, with a new script and figure (`correlated_noise.py`): correlation with each neighbour, and the shortfall against box size. They also cover what would have to be different: measure the factor and widen the error bars, carry the covariance in the noise model, or work on unresampled exposures. The 4.4 closure states the argument plainly too.
