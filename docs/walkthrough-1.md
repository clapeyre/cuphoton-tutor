# Walkthrough 1 · Unit 00

Rough notes are fine. Put the lesson number first, and the time if you can.

## 0.1
Okay, this starts a bit abruptly. I think a human would expect a little bit more of an intro to what it is we're doing here and what we're talking about. 
Oh, I see the videos talk about modules and not units. Maybe we should use a hybrid and call the breakdown here of learning elements: modules and lessons, like module 00 and lesson 0.1. 
I see the video here. Have you pulled in everything needed to change, edit, generate these videos again, or generate new ones? 
This is a style detail, but I think I would rather have a black-and-white scale for telescope images. It'd be more intuitive.
Also, a content comment, but I think it would be nice to introduce a few links to external resources in the course. For example, when you say that the noise grows as the square root of the counts, I guess that's because the noise follows a Poisson distribution (oh yeah, actually, I see you put it in the image caption). Maybe we could just have a link to the Wikipedia article on Poisson distributions or a link to noise in astrophotography images. I agree that we don't want to spend time explaining this here because that's not the actual topic, but it's also always good to ground the explanation in links to external, more detailed explanations where we can. 
Oh, wait, it's more than a detail, I guess. The question you're asking is interesting for thinking out loud. What's a little worrying to me is that there isn't really enough information on the page to answer it, or I guess it depends on the background you have for this information.

If you already know what a Poisson distribution is and how it behaves, then you can infer that the noise is going to grow more slowly than the observation, like the signal. If you don't know that, you can't really guess it.

Now, that's not necessarily a problem. I like the idea of working with an AI tutor like this: there are several layers to the answers. There's no pure right and wrong answer. The student, anyway, doesn't get graded on it. It's more like it's good if they get the intuitive part right, and then the answer itself can be a little bit richer because it's also telling you things about engineering concepts that aren't entirely explained on the page but are still relevant. 

What's maybe a bit more of a problem relates to the very first point about starting abruptly: we're still not quite sure what it is we're trying to do here. Well, okay, no, that's not true. The video is here to explain it, so thanks to the video, we have an inkling.

The question itself at the bottom, "If the exposure time is twice as long," I would tend to ground that a little bit if I talked to students. Instead of just asking a totally open-ended question like this, I would say something like, "In astrophotography, you like to have long exposure times if you can. Let's try to think through why and what that does to signal-to-noise." Something like that, to tell the learners why we're asking this question at all. 

Oh, what would be cool is to have the tutor answer stream, because otherwise you don't really know how long you're going to wait until it answers. I mean, obviously, there are still going to be the thinking tokens and some latency, but I think people, when they're having a dynamic interaction with an AI, like the streaming behavior. 

Yeah, I'm trying to answer the first question, and going back to the thing with Poisson, I don't really like the way it's interacting with me. I put in an answer that basically is careful, but it would be the answer of someone who doesn't really know what the Poisson distribution is going to be doing. That's actually a complicated concept to figure out: why exposure time won't make noise scale linearly, and we don't really want to get into the details of why.

People might know because you have some experts taking this course, and people might not know. Here, the tutor is trying to just reformulate the question again until I get it right. Fundamentally, if I don't know the concepts here, I don't have enough on the page to guess that the noise is going to scale as the square of exposure time. 

 well, now that I'm at the end of the interaction with the agent, I'm not even so sure about what I said before anymore. Is it because it's a Poisson distribution that it's a square root? I'm not even sure. Yeah, there's something. Okay, maybe I just didn't get it right, and the tutor actually did just bring me to the right conclusion. Huh, interesting. I don't know 

But what's really important as an educator is to help students reflect on the result, not the result itself. "We found" / "Which Raises"  is a fundamental part of the educator's job, but it's a bit terse and bland here. if I taught this, I would be very insistent on the fact that this is the fundamental reason why, when we're doing astrophotography, we focus a lot on increasing exposure time
 
## 0.2
 I like that there are key terms that you can get more explanations for, but I don't really like that they're inline because it changes the whole formatting of the page after it. Visually, it's a bit jarring to have this jump every time. I think having a tooltip approach would be better 
 it's a little random to say this here, but I'm looking at the run record, which shows where the files were actually written. I don't know. This is making me thoughtful.

I think that if you're on a platform like Khan Academy or Brilliant, obviously there is no file system. You're purely in a cloud configuration, but more than cloud, it's more like you're abstracted away from the file system. I don't know if we want to do that, be totally abstracted away from the file system, because in the end, even though specifically for this course we've moved away from the code, we are still teaching people code.

The problem is that having a file browser in the web browser can be tricky. Part of me would like to have it, though: just a widget somewhere where you see the files and you see new files as they appear. Then again, the files used for explanations, the whole organization is agentic, and you don't really want to have to worry about it. If you saw the files, you would probably also need to be able to open them, and that is another can of worms: how do you want to look at code? How do you want to look at pictures or images?

I don't know. Maybe let's not act on this at all for now. Maybe I just need to get comfortable with the fully cloud-like interface. By definition, users will have, at least for now, in its current form, started the server at some point somewhere, and so that simple act means that they were able to pull a folder and navigate to it. They can look at things once it's done, so the connection is there, even though it has a bit more friction than the great interface we're building 

I don't see any bullet points in the text for the lessons, and in 0.2, the first paragraph would be easier to read with some bullet points. I think something that says:

* Something in the sky really changed.
* The observing conditions changed.

Right now, it's actually not 100% obvious while reading it that there's this dichotomy

I see the tutor sometimes respond with a bit of Markdown, at least with double stars for bold text.  that doesn't seem to be rendered at the moment 

## 0.3
 I wonder, when there are several questions one after the other on a page, if we should maybe show them progressively, like make them appear. I don't know if there's a lot of value in showing everything at once and letting people skip ahead, because there's little text there anyway. The experience is really through the back-and-forth with the agent and understanding as you go, so maybe we should just make things appear progressively as we progress through the page 
## 0.4
 looking at this lesson, I think I might want to amend my comment from before a little bit. In this case, maybe a tooltip would still work for the xrep, xpoise, and so on. It does kind of make sense here to open up this actual box on the page more, at least than when we're opening something in the middle of a sentence. That was very strange, but even still, actually, it's not super obvious right now.

After I move my mouse away after having clicked on one of them, it doesn't highlight which one is currently selected, so you have to read to figure that out. I guess the problem also with my tooltip approach is you can't easily click the link inside the explanation, which brings you to ask the tutor more.

Then again, do we need that? The tutor is always open on the right and says, "Ask about anything on this page." I could just go there and say, "What's xrep again?" or something, and/or "Tell me why xrep does alignment and how it actually works," or something. Maybe we don't need that, and we could try pure tooltips. I'm not sure 
## Overall
 I know I've said a lot here, and that can come across as critical, but I know you won't get offended. My overall assessment is that this is amazing. I feel like a lot of people could understand what we're talking about thanks to this, and the experience is really good. The agent turns and the summarization at the end could be slightly fine-tuned, especially if you move to complex material. You're going to have to be careful about the narration and everything, but man, I just really like it overall
---

## What changed in response (13 Nov)

Your session is archived in `runs/learner-1113-134514-walkthrough-1/` (with a copy of these notes).

- **Abrupt start.** Each module's first lesson now opens with an introduction
  (`intro:` in `module.yaml`): what the course is, what this module does, and how the page works.
- **Modules, not units.** Renamed everywhere: the page, the tutor's prompt, the content
  (`course/modules/*/module.yaml`).
- **Video sources.** The full pipeline is now in `media/` (`media/README.md`): scripts, Manim
  scenes, narration, data steps and `setup.sh`. It was checked by regenerating v1 end to end.
  v1 and v2 in the repo were older drafts; both are now re-rendered from the current scripts.
- **Grey scale.** The tutor's contract and lesson notes ask for grey scale on sky images, and
  for grey centred on zero on difference images. The 0.4 dipole figure was regenerated
  (`make_dipole.py`).
- **External links.** Lessons can use `[text](https://…)`. Glossary entries take
  `read_more: "Label | URL"`, shown in the definition. Links added for Poisson, shot noise,
  signal-to-noise, seeing, PSF, image registration, FITS, WCS, Alard & Lupton.
- **0.1 not answerable from the page.** The page now states the √N rule with numbers and a
  link. The question is grounded ("astronomers fight for exposure time, let's see why") and
  asks whether the source is easier to see. The tutor notes and contract now say: when a
  learner stalls on a premise, give it in one sentence and don't run a question ladder;
  accept intuition, no grades.
- **Streaming.** Tutor replies in Your-turn boxes and in the margin stream as they're
  written. The tutor now answers in plain text, which goes straight to the box.
- **Bland closures.** A closure now has "What we found", "Your answers, in short" (the
  settle summaries), "Why it matters", and "Which raises". The tutor also adds a line on why
  the answer matters when it settles. All four Module 00 closures were rewritten (0.1 now
  makes the long-exposure point).
- **Inline definitions jump the page.** They're now popovers anchored to the term; Esc or a
  click outside closes them.
- Also: "pointing" is now a defined term in 0.2 (you asked "What's pointing?"). Tutor
  messages render bold, code and term look-ups.
