#!/usr/bin/env python3
# hardgit.py: Force-sync the current repo to the remote default branch.
# WARNING: This discards ALL local commits and changes. It also removes ignored files.

import subprocess
import sys

def run(cmd, check=True):
    """
    Run a shell command and return its combined stdout+stderr as text.
    Raise RuntimeError if the command fails when check=True.
    """
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode != 0:
        raise RuntimeError(f"$ {' '.join(cmd)}\n{p.stdout}")
    return p.stdout.strip()

def ensure_git_repo():
    """Exit if Git is missing or the current directory is not a Git repo."""
    try:
        run(["git", "--version"])
        run(["git", "rev-parse", "--is-inside-work-tree"])
    except Exception as e:
        print("Not a Git repository, or Git is not installed.", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

def pick_remote():
    """Choose a remote. Prefer 'origin', else use the first remote found."""
    remotes = run(["git", "remote"]).splitlines()
    if not remotes:
        print("No remotes found. Add one: git remote add origin <url>", file=sys.stderr)
        sys.exit(1)
    return "origin" if "origin" in remotes else remotes[0]

def remote_has_branch(remote, name):
    """Check if the remote has the given branch name."""
    out = run(["git", "ls-remote", "--heads", remote, name])
    return bool(out.strip())

def get_remote_default_branch(remote):
    """
    Detect the remote default branch.
    Try the remote HEAD symbolic ref.
    Fall back to 'main' then 'master'.
    Else pick the first remote head.
    """
    # Method 1: origin/HEAD -> origin/main
    try:
        sym = run(["git", "symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD"])
        return sym.split("/", 1)[1]  # "origin/main" -> "main"
    except Exception:
        pass

    # Method 2: common names
    if remote_has_branch(remote, "main"):
        return "main"
    if remote_has_branch(remote, "master"):
        return "master"

    # Method 3: pick any existing remote head
    heads = run(["git", "ls-remote", "--heads", remote]).splitlines()
    if not heads:
        print(f"Remote '{remote}' has no branches.", file=sys.stderr)
        sys.exit(1)
    # Line format: "<sha>\trefs/heads/<name>"
    first = heads[0].split("\t")[-1]
    return first.rsplit("/", 1)[-1]

def local_branch_exists(branch):
    """Return True if the local branch exists."""
    p = subprocess.run(["git", "rev-parse", "--verify", branch],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p.returncode == 0

def switch_branch(branch):
    """Switch to the given branch. Support older Git with checkout."""
    try:
        run(["git", "switch", branch])
    except Exception:
        run(["git", "checkout", branch])

def main():
    ensure_git_repo()

    remote = pick_remote()
    print(f"[1/6] Remote: {remote}")

    print("[2/6] Fetching from remote and tags...")
    run(["git", "fetch", remote, "--tags", "--prune"])

    branch = get_remote_default_branch(remote)
    rb = f"{remote}/{branch}"
    print(f"[3/6] Target: {rb}")

    try:
        head_before = run(["git", "rev-parse", "--short", "HEAD"])
    except Exception:
        head_before = "N/A"

    if local_branch_exists(branch):
        print(f"[4/6] Switching to local branch {branch}...")
        switch_branch(branch)
    else:
        print(f"[4/6] Creating local branch {branch} from {rb}...")
        run(["git", "checkout", "-B", branch, rb])

    print("[5/6] Hard resetting to the remote target...")
    run(["git", "reset", "--hard", rb])

    print("[6/6] Cleaning untracked and ignored files (-fdx)...")
    run(["git", "clean", "-fdx"])

    head_after = run(["git", "rev-parse", "--short", "HEAD"])
    print(f"Done. HEAD {head_before} -> {head_after}")
    print(run(["git", "status", "-sb"]))
    try:
        print(run(["git", "log", "--oneline", "-n", "5"]))
    except Exception:
        pass

if __name__ == "__main__":
    main()
