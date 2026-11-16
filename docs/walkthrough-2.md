# Walkthrough 2 · Module 01 (and anything you re-check in 00)

Rough notes are fine. Put the lesson number first, and the time if you can.
I find it interesting that we can now look at the run record and even the actual code inline. I think it would be really good if it had a bit of syntax highlighting, though, because it can be a bit hard to read right now. 

## 1.1

## 1.2

## 1.3

## 1.4

## 1.5

## 1.6
When the agent has a few things to do, sometimes it outputs text, and then it's thinking about creating an image or something. When the image is ready, it displays it and then adds some text.

I don't think I see any visual marker of the fact that it's still thinking, so sometimes it's a little bit weird. I see the first part of the answer, and it's clearly not done, but I don't have any visual cue for the fact that the agent is still working. I'm wondering what I should do, if I should type something else in or not, and then suddenly the rest of it comes up.

Adding a visual cue for when the agent is doing multi-turn outputs to screen but it's still working would be useful. 
## 1.7
This is really cool. There was just a little unfortunate thing at the beginning there, where I was instructed to ask to run the colleague's script, and then it said that it had already run. Then it showed me the result. It wasn't perfectly smooth, but it went ok.
The fact that you can select anything on the page and it gets moved to the focus in the little "Ask about anything" area is really cool. It actually becomes annoying in some questions, like the one where I have to write a bit of code. When you write code, you often want to go back and select something, copy, paste, and so on. I can't because every time I copy or paste something, it takes my cursor out. Maybe it doesn't make that much sense to enable this feature inside the editable cells. If there is a way to not do that inside editable cells, I think that would be good. Although, now that I think of it, I don't even know if it's good to leave it in the text. If you think about trainings that are a little bit more code-heavy, students might also want to go up and copy-paste parts of code that have been shown (or function names or things like that) directly in the course material so that they can answer a question. If, each time, the cursor jumps away, that's going to be very annoying. Let's maybe just let people copy-paste the part that they want to send to the side manually if they really need to.  
## Overall

---

## What changed in response (16 Nov)

- **Syntax highlighting:** Python and shell code in run records and in tutor
  messages is highlighted (highlight.js, `web/src/Code.tsx`).
- **No cue while the tutor is still working (1.6):** the server now says which
  Your turn the tutor is on. Between messages (running code, placing a figure)
  the turn shows "The tutor is running code / placing a figure / thinking" until
  it's done. In the margin, text written before a tool call is now kept as its
  own message; before, it was lost.
- **1.7 "I already ran it":** the 1.7 notes told the tutor to run the script, so
  it did so on open, in a reply the page never shows. The notes now say to
  wait, and the contract says never to start a turn's work on open nor refer
  back to text the learner never saw. Retested: it does nothing on open and
  runs the script when asked.
- **Selecting text jumps to the margin:** removed. Copy and paste work
  normally; figures and videos keep their "Ask about this" links. The Module 00
  intro no longer mentions selecting.
