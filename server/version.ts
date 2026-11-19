// Which version of the course app this server runs: the git commit it was started from. Feedback is only
// readable if we know what the learner was running (a launchable tracks main, so two learners who start
// minutes apart can be on different commits). Read once at startup; stamped on feedback notes, metrics,
// the admin page and the report archive.
import { execFileSync } from "node:child_process";
import { ROOT } from "./config.ts";

const git = (...args: string[]) => {
  try { return execFileSync("git", ["-C", ROOT, ...args], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim(); }
  catch { return ""; }
};

const commit = git("rev-parse", "--short=10", "HEAD");
// Local edits to tracked files: the commit alone doesn't say what ran.
const dirty = commit !== "" && git("status", "--porcelain", "--untracked-files=no") !== "";

// Where "Report on GitHub" opens a new issue: CUPHOTON_LEARN_ISSUES_URL, else the GitHub repo this copy
// was cloned from (a fork reports to the fork), else the course's own repo.
function issuesUrl(): string {
  if (process.env.CUPHOTON_LEARN_ISSUES_URL) return process.env.CUPHOTON_LEARN_ISSUES_URL;
  const m = git("remote", "get-url", "origin").match(/github\.com[:/]([^/]+)\/([^/]+?)(?:\.git)?$/);
  return m ? `https://github.com/${m[1]}/${m[2]}/issues/new` : "https://github.com/clapeyre/cuphoton-tutor/issues/new";
}

export const app = {
  commit: commit || "unknown",
  dirty,
  date: git("log", "-1", "--format=%cs"),
  /** What to print and stamp: the commit, "+changes" if tracked files were edited. */
  label: commit ? commit + (dirty ? "+changes" : "") : "unknown",
  issues: issuesUrl(),
};
