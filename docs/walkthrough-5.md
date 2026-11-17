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
# Second pass
## 4.5
 another comment about long threads when they occur is that it's not always easy to see right now which turns are from me and which ones are from the tutor. It says so, but it's a small gray input, and there's a slight difference in the background color between the two. I don't know how we could make that more visible.

Maybe we could do it a little bit like an SMS conversation. I don't know if that would be too heavy, though. At least, using up only 90% of the width, for example, and left-justifying what the tutor says and right-justifying what we said. It feels to me like that would be intuitive to people because that's also what it looks like when we have a conversation with a lot of AIs today. Maybe it would be too clunky here, so I don't know. Maybe we need to just try.  actually, I just checked the interfaces for Claude and ChatGPT, and both of them do something a little different from what I said. In the sense that they are full width for the answer by the AI, but they do right-justify the text that I send, that is intuitive enough. Maybe this would be good here too.

The difference is that I tend to pour my heart out in these exchanges, and with the tutor, it's not so unbalanced. When I talk to ChatGPT or Claude, usually my prompt is relatively short compared to the huge reply I get, which I guess is the justification for using the full width for the full replies. With the tutor here, it's not so clear. There are a lot of turns where I actually speak as much or more than the tutor does 

 also, a general comment on 4.5 is that this was very enlightening in the sense that it would make me extremely cautious of my preconceptions. Instead of barging in and saying, "Oh, more data is going to be better," all the hypotheses we made before might have to be revisited. That point was very well conveyed by the example.

I just have to say, on top of that, that it's not a very satisfying example because, in the end, we just end up saying that, well, we made it worse. We just added more false detections, so it's not a super selling point for the stacking software itself. I guess people can extrapolate pretty well from there that this would work well in other cases and that, if you're careful enough to use it at the right moments, then it would be useful.

Just wanted to keep a small note here on the fact that it's a little bit unsatisfying to have basically something that we spend a long time showing doesn't work 

## 4.6
Oh, I've got another UI observation, which is that I think the very top row and the left navigation list should probably move when we scroll down. it's more obvious now that I'm in lessons like the 4.6, where it keeps referring back to previous lessons. I keep switching from one to the other and having to scroll back up just to find that, which is a bit weird 

Okay, we're going to have to log somewhere some of the reasons why I find this way of learning absolutely amazing, but this 4.6 is clearly showing one of them: the fact that you have held my hand, trained the model, tested it, showed me the results on the test set, then changed the data, retrained the model to get better results. All of that in a single conversation without me ever seeing the code is absolutely amazing.

I think that if I were to teach this course to astronomers, 20% of what I would be trying to convey is the fact that QPhoton can do data processing fast. 80% of it would be a plea telling them: please stop opening your Python text editor when you're starting data processing and spending a week doing what you could do in 20 minutes having a chat with your agent. Wow, this needs to be put front and center of the value add, especially when I'm going to talk about this endeavor internally

## What changed in response (second pass, 17 Nov)

- **Your messages on the right.** In every conversation (turns and side trips), your messages now sit on the right, at most 88% of the width, with a green tint and border and a green "You". The tutor's stay full width. With long messages on both sides, the alignment carries the difference, as in Claude and ChatGPT.
- **The course map stays in view.** The left list now stays put while the lesson scrolls, like the top row and the margin, so jumping back to 4.2 from deep in 4.6 is one click. (The top row already stayed; on a narrow window the map still scrolls away, since it sits above the lesson there.)
- **4.5 now ends on when stacking pays, with numbers.** The closure and the tutor notes now use the noise budget the learner just measured. Stacking N nights divides the reference's share of the difference's noise by N. Here the share was 5%, so three nights could gain at most 2%. Where the reference supplies half the noise (no sharper than the target, about as deep), three nights cut the noise by 18%, about 0.2 magnitudes deeper; ten nights, 26% and 0.3 magnitudes. That's why surveys build deep references. The takeaway becomes "measure the share before you stack", and the notes say xRep did its part right; what failed was the prediction.
- **Could 4.6's classifier rescue 4.5's extra sky?** I tried it with your two trained models on the stack's 11 new-area hotspots: no. The first calls 3 of 11 real, the retrained one 4, and not the same ones. Residues from a reference blurrier than the target are another kind of bogus neither model trained on, the same lesson as the cosmic rays. That's now a fact in the 4.6 tutor notes, in case a learner asks.
- **Why this way of learning.** Your words are in `docs/WHY.md`, with what happened in the 4.6 conversation, for talks about this course. Putting "work with your agent instead of opening an editor" front and centre in the course is step 3 of `docs/ROADMAP.md`, with candidate places (Module 00's opening, 4.6's closure, 6.1). The framing is yours to decide, so I haven't rewritten any lesson for it.

