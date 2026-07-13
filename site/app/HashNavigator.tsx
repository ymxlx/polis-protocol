"use client";

import { useEffect } from "react";

export function HashNavigator() {
  useEffect(() => {
    const jumpToHash = () => {
      if (!window.location.hash) return;
      const id = decodeURIComponent(window.location.hash.slice(1));
      document.getElementById(id)?.scrollIntoView({ behavior: "auto", block: "start" });
    };

    const frame = window.requestAnimationFrame(jumpToHash);
    window.addEventListener("hashchange", jumpToHash);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("hashchange", jumpToHash);
    };
  }, []);

  return null;
}
