# Walkthrough 3 · Module 02

Rough notes are fine. Put the lesson number first, and the time if you can.

## 2.1
I'm still seeing two turns, like two boxes for which I'm going to have to give an input at the same time, even though I think in the progression I'm not supposed to answer both. I'm really supposed to work on the first one first, and then, when it's valid, I can move on to the second. Didn't we say at some point that we were going to make it so that those appear one after the other? 
## 2.2
Do you think it would be possible to make it so that when we've typed text into a box (like for an upcoming turn with an agent) but we have not submitted it (so not pressed Enter), then if we switch to another tab to check something and then come back, it doesn't erase it? I can imagine students getting bitten by that over and over again. 
## 2.3
Something a bit weird happened where it closed the first "Your Turn" box, but it was actually still generating an output when I tried to open it to see the conversation. Inside, it did a transition towards the next question, even though that next question is already on screen. It should have stopped, I think, once it was done treating the ongoing question, but it continued and said, "Now the laptop case," and so on. We already have that in the intro to the next "Your Turn" box, which is on the laptop with no usable GPU, blah blah blah. 
## 2.4
I see that there is a specific font that's been used to show the bash command, and that's good, but I think it's a little too subtle at the moment. We should highlight code a little better.

In fact, this is not related to this specific page, but I also thought that it would be good to have some MathJax rendering of math equations. When we're building the courses, that would often be helpful for readability. Maybe it's already implemented, and I just didn't see it because there are none in this course, but I wanted to mention it. 
## 2.5

## 2.6

## Overall
I'm not inclined to remove this at this moment because this is all an interesting experiment, but long term, I think module 02 is a little strange. It feels very anecdotal to the way the CLI works right now in QPhoton. If the CLI changed its behavior just slightly, you would have to reforge this entire module. This is nothing bad, but let's just say that some parts of this course seem more pertinent than others for the whole endeavor. Then again, it's true that a lot of people that come to these trainings actually get snagged on some very basic things, so hammering these details isn't necessarily a bad use of time. 
---

## What changed in response (16 Nov)

- **2.1, two turns open at once:** turns now open one at a time. A later turn
  shows only its title and "Opens once you've finished the one above" until
  the earlier ones are settled.
- **2.2, unsent text lost:** what you type in a Your-turn box or the margin is
  kept in this browser until you send it, across lessons, tabs and reloads.
- **2.3, the tutor ran on into the next question:** a turn stays open while
  the tutor is still writing in it, even after it settles. The settle tool now
  tells the tutor to finish and stop, and the contract forbids leading into the
  next turn.
- **2.4, code too subtle:** inline code is a visible chip; lessons can have
  fenced code blocks (the 2.4 command is one), framed and highlighted.
- **Maths:** KaTeX renders `$…$` and `$$…$$` in lessons and tutor messages.
  First uses: σ ≈ √N in 0.1, S/N ∝ √t in its closure, the variance formula
  in 1.2.
- **Videos:** the three videos are re-rendered in grey, like the figures.
- **Overall (Module 02 is tied to today's CLI):** parked in `docs/BACKLOG.md`,
  with two ideas for making it less brittle.
