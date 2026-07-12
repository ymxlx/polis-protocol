"""Amendment management for the Polis Protocol.

This module implements listing, voting on, and tallying amendments.
Proposed amendments live in `_polis/amendments/proposed/` and ratified ones
live in `_polis/amendments/ratified/`.
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from ._io import atomic_write_text
from .routing import parse_frontmatter, load_citizens, load_citizen_status


def load_amendment(path: Path) -> tuple:
    """Read an amendment file and parse its frontmatter and body."""
    text = path.read_text(encoding="utf-8")
    return parse_frontmatter(text)


def list_amendments(polis_root) -> list:
    """Return all proposed and ratified amendments sorted by ID."""
    root = Path(polis_root)
    out = []
    
    # Proposed
    d_proposed = root / "amendments" / "proposed"
    if d_proposed.exists():
        for f in d_proposed.glob("*.md"):
            fm, _ = load_amendment(f)
            if fm:
                out.append(fm)
                
    # Ratified
    d_ratified = root / "amendments" / "ratified"
    if d_ratified.exists():
        for f in d_ratified.glob("*.md"):
            fm, _ = load_amendment(f)
            if fm:
                out.append(fm)
                
    return sorted(out, key=lambda a: a.get("amendment_id", ""))


def vote_amendment(polis_root, amendment_id, citizen, vote, rationale=None, now=None) -> dict:
    """Cast or update a vote on a proposed amendment."""
    root = Path(polis_root)
    if vote not in ("agree", "disagree", "abstain", "request_changes"):
        raise ValueError("Vote must be 'agree', 'disagree', 'abstain', or 'request_changes'.")
        
    citizens = load_citizens(root)
    if citizen not in citizens:
        raise ValueError(f"Unknown citizen: '{citizen}'")
        
    f = root / "amendments" / "proposed" / f"{amendment_id}.md"
    if not f.exists():
        if (root / "amendments" / "ratified" / f"{amendment_id}.md").exists():
            raise ValueError(f"Amendment '{amendment_id}' is already ratified.")
        raise ValueError(f"Amendment '{amendment_id}' not found in proposed amendments.")
        
    fm, body = load_amendment(f)
    if fm.get("status") != "proposed":
        raise ValueError(f"Amendment is in status '{fm.get('status')}' and cannot be voted on.")
        
    votes = fm.setdefault("votes", {})
    # Remove citizen from all categories first
    for cat in ("agree", "disagree", "abstain", "request_changes"):
        votes.setdefault(cat, [])
        if citizen in votes[cat]:
            votes[cat].remove(citizen)
            
    # Add citizen to the chosen vote category
    votes[vote].append(citizen)
    
    # Strip any existing response block for this citizen from the body
    body_lines = body.splitlines()
    new_lines = []
    skip = False
    for line in body_lines:
        if line.startswith(f"## Response from {citizen}"):
            skip = True
            continue
        if skip and line.startswith("## Response from "):
            skip = False
        if not skip:
            new_lines.append(line)
    body = "\n".join(new_lines).rstrip()
    
    # Append the new response block
    resp = f"\n\n## Response from {citizen} ({vote})"
    if rationale:
        resp += f"\n{rationale.strip()}"
    body += resp
    
    content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body + "\n"
    atomic_write_text(f, content)
    
    # Chronicle entry
    now = now or datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    chron = root / "chronicle.md"
    note = rationale.replace("\n", " ").strip() if rationale else "-"
    chron_line = f"- {ts} | {citizen} | voted on amendment | [[amendments/proposed/{amendment_id}]] | {vote}: {note}\n"
    
    existing = chron.read_text(encoding="utf-8") if chron.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    atomic_write_text(chron, existing + chron_line)
    
    return {"ok": True, "amendment_id": amendment_id, "votes": votes}


def tally_amendments(polis_root, proposer_or_default_citizen="polis-tally", now=None) -> list:
    """Scan proposed amendments and ratify, reject, or expire them based on votes."""
    root = Path(polis_root)
    now = now or datetime.now()
    fourteen_days_ago = now - timedelta(days=14)
    
    # 1. Determine active citizens from chronicle
    active_citizens = set()
    chron = root / "chronicle.md"
    if chron.exists():
        for line in chron.read_text(encoding="utf-8").splitlines():
            if line.startswith("- ") and "|" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 2:
                    ts_part = parts[0].lstrip("- ").strip()
                    try:
                        ts = datetime.strptime(ts_part, "%Y-%m-%d %H:%M")
                        if ts >= fourteen_days_ago:
                            active_citizens.add(parts[1])
                    except ValueError:
                         pass
                         
    # Filter only known citizens and check they are not away
    citizens = load_citizens(root)
    active_citizens = {c for c in active_citizens if c in citizens}
    filtered_active = set()
    for c in active_citizens:
        status = load_citizen_status(root, c)
        if status.get("state") != "away":
            filtered_active.add(c)
    active_citizens = filtered_active
    
    # Default quorum: simple majority of active citizens, min 2
    default_quorum = max(2, (len(active_citizens) // 2) + 1)
    
    proposed_dir = root / "amendments" / "proposed"
    if not proposed_dir.exists():
        return []
        
    results = []
    for f in sorted(proposed_dir.glob("*.md")):
        fm, body = load_amendment(f)
        if fm.get("status") != "proposed":
            continue
            
        aid = fm.get("amendment_id") or f.stem
        votes = fm.setdefault("votes", {})
        agree_list = votes.setdefault("agree", [])
        disagree_list = votes.setdefault("disagree", [])
        abstain_list = votes.setdefault("abstain", [])
        req_changes_list = votes.setdefault("request_changes", [])
        
        quorum_needed = fm.get("quorum_required")
        if quorum_needed is None or quorum_needed == 0:
            quorum_needed = default_quorum
            
        agrees = len(agree_list)
        
        # A. Check Ratification
        if agrees >= quorum_needed:
            fm["status"] = "ratified"
            fm["ratified_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
            
            ratified_dir = root / "amendments" / "ratified"
            ratified_dir.mkdir(parents=True, exist_ok=True)
            dest = ratified_dir / f.name
            
            content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body + "\n"
            atomic_write_text(dest, content)
            f.unlink()
            
            # Chronicle entry
            ts = now.strftime("%Y-%m-%d %H:%M")
            title = fm.get("title", aid)
            chron_line = f"- {ts} | {proposer_or_default_citizen} | ratified amendment | [[amendments/ratified/{aid}]] | {title}\n"
            existing = chron.read_text(encoding="utf-8") if chron.exists() else ""
            if existing and not existing.endswith("\n"):
                existing += "\n"
            atomic_write_text(chron, existing + chron_line)
            
            results.append({
                "amendment_id": aid,
                "action": "ratified",
                "detail": f"met quorum ({agrees}/{quorum_needed})"
            })
            continue
            
        # B. Check Expiry
        expires_at_str = fm.get("expires_at")
        expired = False
        if expires_at_str:
            try:
                exp_date = datetime.strptime(expires_at_str.strip(), "%Y-%m-%d").date()
                if now.date() > exp_date:
                     expired = True
            except ValueError:
                 pass
                 
        if expired:
            fm["status"] = "expired"
            content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body + "\n"
            atomic_write_text(f, content)
            
            # Chronicle entry
            ts = now.strftime("%Y-%m-%d %H:%M")
            title = fm.get("title", aid)
            chron_line = f"- {ts} | {proposer_or_default_citizen} | expired amendment | [[amendments/proposed/{aid}]] | {title}\n"
            existing = chron.read_text(encoding="utf-8") if chron.exists() else ""
            if existing and not existing.endswith("\n"):
                existing += "\n"
            atomic_write_text(chron, existing + chron_line)
            
            results.append({
                "amendment_id": aid,
                "action": "expired",
                "detail": f"deadline passed ({expires_at_str})"
            })
            continue
            
        # C. Check early rejection (cannot possibly reach quorum)
        # Any active citizen who hasn't voted yet is a potential agree
        all_voted = set(agree_list + disagree_list + abstain_list + req_changes_list)
        active_non_voters = [c for c in active_citizens if c not in all_voted]
        max_possible_agrees = agrees + len(active_non_voters)
        
        if max_possible_agrees < quorum_needed:
            fm["status"] = "rejected"
            content = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n" + body + "\n"
            atomic_write_text(f, content)
            
            # Chronicle entry
            ts = now.strftime("%Y-%m-%d %H:%M")
            title = fm.get("title", aid)
            chron_line = f"- {ts} | {proposer_or_default_citizen} | rejected amendment | [[amendments/proposed/{aid}]] | {title}\n"
            existing = chron.read_text(encoding="utf-8") if chron.exists() else ""
            if existing and not existing.endswith("\n"):
                existing += "\n"
            atomic_write_text(chron, existing + chron_line)
            
            results.append({
                "amendment_id": aid,
                "action": "rejected",
                "detail": f"cannot meet quorum (max possible agrees: {max_possible_agrees}/{quorum_needed})"
            })
            continue
            
    return results
