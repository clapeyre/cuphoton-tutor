# Walkthrough 6 · Module 05 (and 06)

Rough notes are fine. Put the lesson number first, and the time if you can.

## 5.1
There was something slightly misleading about the course that told me to ask to see the survey block of the config file. When I did that, I just followed blindly, but I didn't realize that there's actually more to that config file. I had to run it to realize something was wrong, and then I was looking everywhere in the survey block for what I could have done wrong. Actually, the part that was important was outside of it.

Maybe that's just a small adjustment to the text, or one way to say that. This is actually leading me down another path, which is: I do wonder, when we start working with files like this, how much it makes sense to always go through the agent to show us the file. As opposed to looking at the actual file, I think maybe it could make sense to have some way to actually see the full file somewhere, maybe as a hovering window above the main window or something. Sometimes just getting it at a glance is useful, even if you can then go back and chat with the agent to dig into the different sections and so on.

Here, it was invisible, and because I was only told to look at one section, that's what the agent pulled, and I never realized there was more. You would expect people, especially for a config file, to edit that as text in a text processor, not necessarily go through their agent to edit it.

I don't know if we should implement a read/write file reader, because that sounds icky and like it could go wrong in different ways, especially through a browser. I don't know unless you think it's feasible, but maybe we should stick to just read-only, and then you have to go through your agent to tell it what you want to actually put in the file for the run. At least being able to click and open and feel like I'm seeing the whole file at a glance, and I can scroll through it up and down and so on (ideally with some syntax highlighting), would be really great. 
## 5.2

## 5.3
Oh, okay. I'm watching the video here on 5.3, which is really cool, and I think I'm finally understanding some of the things that the tutor tried to explain to me a while back. I'm not sure when. Maybe it was in module 4. It had long explanations about noise and reprojecting to a grid and how that changed the noise, but the excellent visual representation in the video here in 5.3 helps a lot with understanding what that was about. 
## 5.4
One list in the first discussion on this page, one output Markdown list, didn't show up correctly. The dashes appeared inline. In fact, I'm not sure I've ever seen a bulleted list come up in the tutor's responses, so I don't know if the markdown is rendered correctly at the moment. I did see some math equations being rendered, and those look good. 

Looking at it more closely, it seems that when the agent is talking about chi-squared in the text outside the conversations, it uses the Greek letter. When it's using it in conversations, it's writing it out in the Latin alphabet (chi). Maybe there's a difference in Markdown rendering between the two. 

This is a simple UI observation, but once the conversation has become long, it would actually be quite useful to have a way to close a finished conversation that I opened up again for evaluation, analysis, check, whatever. It would be useful to close it from the bottom and not have to scroll all the way back up to the top of it to close it. 
## 6.1

## Overall

## What changed in response (17 Nov)

- **A Files panel (5.1).** A Files button, top right, opens a window over the page with your module's work folder: line numbers, syntax highlighting for Python, YAML and JSON, figures full size, exported reports in a new tab, a filter, and a folder picker for other modules. It's read-only, as you suggested; changes still go through the tutor. A file name the tutor writes in backticks (`config.yaml`, `run1/summary.json`) is now a link that opens it there. The tutor's instructions say to point to files by name instead of pasting them. Editing in the panel, and showing course data, FITS headers or Parquet tables, are parked in `BACKLOG.md`.
- **5.1's wording.** The lesson no longer says to look at the survey block. It says the tutor copies the shipped configuration into your work folder when it prepares the lesson, to read it whole in Files, and that the other blocks make decisions too, through their defaults. That last part is a fair hint at the trap, not the answer: `psf_sigma_px: null` still looks harmless until the run.
- **Lists in tutor messages (5.4).** You were right: tutor messages only knew paragraphs, so every list the tutor ever wrote ran together. Bulleted and numbered lists and short headings now render, including a list right under its lead-in line. Bold text with code inside it (**Kernel `chi2/dof`**) now shows the code properly too.
- **chi2 vs χ² (5.4).** Not a rendering difference: the tutor wrote `chi2/dof`, the name of the field in the run summary, as code, while the lessons write χ²/dof. The tutor is now told to write χ²/dof in prose and keep `chi2` for quoting a field name.
- **Closing a long conversation from the bottom (5.4).** A reopened conversation now has "Hide the conversation" at its end as well. Hiding scrolls you back to the turn's title.
- **The video in 5.3.** Glad it landed. The 4.4 tutor notes already offer it once the error-bar question is settled; 4.4's closure now links to it too, so it's there even if the tutor doesn't offer it.

