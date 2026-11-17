# Walkthrough 4 · Module 03

Rough notes are fine. Put the lesson number first, and the time if you can.

## 3.1
Okay, yeah, 3.1 is leaning a little hard again into the receipt and exactly the fields we need to read, and so on. I'm not sure how much we really need to insist that the users learn the actual field they're going to be reading in the receipt by heart. It's like, "Okay, remember that you have to check your receipts." Fine. Why does the checkpoint have to make me say the precise keyword that I'm going to be looking for in the receipt, again and again? Man, it feels a bit repetitive. 
## 3.2

## 3.3
Okay, I'm looking at the second part that's been added now with XDR. This isn't the first time I'm seeing this in this course, and I actually don't know what the best approach is here. I'm just going to dump my thought process so we can sort it out later.

I think, in a sense, a lot of courses have students open the documentation in parallel. That way, people can just go through the documentation as they move through the course and figure out where things are, and that way it becomes familiar to them. That made a lot of sense in the old world, where you manually went through the documentation and manually coded. Now, we expect people are going to be sending their agents to read the doc anyway, so I don't know how much that makes sense.

When I see questions like the one here, which is asking me to predict what's going to happen for reading losslessly or various compression formats or whatever, it feels to me: maybe I should have better intuitions about this, and I'm off course here. My intuition right now, when I read this, is: oh, I have no way of guessing, but I could look it up in documentation. I don't really know where the documentation is, because I don't think we've ever given the link in the whole course up until now. I could go look for it, but that feels weird and off. If, by module 3, you've never even seen the link to the documentation, you probably are on track to not use it for the entire training.

It would be strange to go look it up, and also I don't want to, because I've gotten used to this world where the agent is holding my hand. I find it awesome, and I don't have to go digging manually for this kind of information. Maybe we don't need to send people to the documentation. It's true that in a number of places I've been surprised by a question of this type: a question asking me to predict something where I feel like it's an arbitrary choice. A read-through of the documentation would solve that, but I don't really want to go read through the documentation. Oh, and by the way, I say cuPhotons documentation, but here I guess I would also need to read AstroPy's documentation. Then again, a lot of people taking this course will already be familiar with AstroPy, so maybe they will be able to do this prediction pretty well. This is mostly a me problem. Maybe the guidance we should give to courses like this is: if the agent asks you to predict something, if you feel like you can, go ahead. If you feel like you can't, then that's fine. Tell it that, and it'll guide you so you understand what's going on. I think I would be fine with that kind of guidance. 
## 3.4
Great and productive discussion in 3.4. Except, I guess this is where my no-code approach is possibly showing at the seams a little bit. The whole thread with the tutor has it clearly referring to the code, but I've never seen it. At some point, it even tells me what I would change in the script. Except, well, this is getting really hard to imagine because I don't see the script. Now, the issue is symmetric. I'm not so sure that we want to see the script because it could have a lot of boilerplate, and it could confuse people. We got to be very careful with what we show. But right now, it is a bit extreme in the sense that I don't think there's any way for me to see the script or any part of it at all. You have to be a pretty good Python developer to just imagine in your head what the script might look like and then suggest changes based on that. 
## Overall
I liked this one. 

---

## What changed in response (16 Nov)

- **3.1, reciting receipt fields:** pass criteria in Modules 02 and 03 now ask
  whether the answer comes from the receipt's evidence, in any words, not for
  field names. 3.1 settles as soon as you've diagnosed it and seen the GPU
  receipt: no extra "one sentence" question. The contract adds: never ask for
  identifiers by heart, never repeat a check the learner has already shown.
- **3.4, discussing code you can't see:** you can ask for the script; the
  tutor shows the timing part verbatim (the whole file if you want), and shows
  changed lines when discussing a fix. General rule in the contract: never
  discuss code the learner can't see; show the few lines that matter. In 1.7
  the code stays hidden until you've named a symptom from the evidence, then
  the stamp-cutting lines are available.

## What changed in response (3.3 second pass, 17 Nov)

- **"I can't predict this" is now a sanctioned answer, as you suggested.** Module 00's "how the page works" says it: when a box asks you to predict and you have nothing to go on, say so, and the tutor will show you where the answer comes from. The tutor's rules say the same: don't push for a guess and don't count it as a failed attempt. Instead, ask what they'd check (the receipt, the guide page), or give the one fact the prediction hinges on and ask again. 3.3's compression prompt now ends "If you have nothing to go on for a file, say what you would look at to find out", and its notes treat "the receipt's `fallback_reason`, `inspect_fits_images`, compare the pixels" as a full answer. Going through every other prediction prompt for the same problem is parked in `BACKLOG.md`.
- **The user guide is now visible from the start.** The top bar links "cuPhoton user guide", and every lesson from Module 01 on shows "In the user guide: <chapter>" under its key terms (3.3: Read FITS images). Module 00's intro says you don't need to read it: the tutor works from it, and it's there when you want the full story. That keeps the agent doing the digging, which is the point you made, while the docs become familiar on the way. The lesson-to-chapter map is a `guide:` line in each lesson's front matter, and the titles come from the pinned checkout.
- **3.4, "I never see the script".** Already addressed since: the tutor shows the lines that matter as an excerpt, and the Files panel (top right) now shows every script in full, read-only.

