"use client";

import { useRef, useState } from "react";

type CopyState = "idle" | "success" | "error";

export function CopyButton({ command, label }: { command: string; label: string }) {
  const [state, setState] = useState<CopyState>("idle");
  const resetTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const copy = async () => {
    if (resetTimer.current) clearTimeout(resetTimer.current);

    try {
      let copied = false;

      if (navigator.clipboard?.writeText) {
        let clipboardTimer: ReturnType<typeof setTimeout> | null = null;
        try {
          await Promise.race([
            navigator.clipboard.writeText(command),
            new Promise<never>((_, reject) => {
              clipboardTimer = setTimeout(() => reject(new Error("Clipboard request timed out")), 900);
            }),
          ]);
          copied = true;
        } catch {
          copied = false;
        } finally {
          if (clipboardTimer) clearTimeout(clipboardTimer);
        }
      }

      if (!copied) {
        const textarea = document.createElement("textarea");
        textarea.value = command;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        copied = document.execCommand("copy");
        textarea.remove();
      }

      if (!copied) throw new Error("Clipboard copy was rejected");

      setState("success");
    } catch {
      setState("error");
    }

    resetTimer.current = setTimeout(() => setState("idle"), 2200);
  };

  return (
    <button className={`copy-button copy-${state}`} type="button" onClick={copy} aria-label={label}>
      <span aria-hidden="true">
        {state === "success" ? "Copied ✓" : state === "error" ? "Copy failed" : "Copy"}
      </span>
      <span className="sr-only" role="status" aria-live="polite">
        {state === "success" ? `${command} copied to clipboard.` : state === "error" ? `Could not copy ${command}. Select the command manually.` : ""}
      </span>
    </button>
  );
}
