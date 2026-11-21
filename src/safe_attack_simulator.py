"""SAFE ransomware-LIKE simulator for IoTShield AI.

SAFE SIMULATION ONLY - NO REAL RANSOMWARE IS RUNNING.

What it does (and ONLY this):
  * creates harmless dummy text files inside a dedicated canonical sandbox folder,
  * "modifies" them by appending a plain-text marker (no encryption, fully readable),
  * renames them with a '.locked_demo' suffix,
  * writes a clearly labelled SIMULATED_RANSOM_NOTE.txt,
  * can reset (recreate) the dummy files at any time.
What it never does: encrypt anything, touch files outside the sandbox, use the network,
persist, spread, hide, or change any system / firewall / routing setting.

Run standalone:  python -m src.safe_attack_simulator --target PLC-01
"""
from __future__ import annotations

import argparse
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SANDBOX_ROOT = PROJECT_ROOT / "demo_sandbox"

BANNER = "SAFE SIMULATION ONLY \u2013 NO REAL RANSOMWARE IS RUNNING."
LOCK_SUFFIX = ".locked_demo"
DUMMY_SUFFIX = ".demo"
NOTE_NAME = "SIMULATED_RANSOM_NOTE.txt"
NOTE_TEXT = (
    f"{BANNER}\n\nThis is a SIMULATED ransom note created by IoTShield AI for a classroom demonstration.\n"
    "No file was encrypted. No data was stolen. No payment is requested. Nothing real happened.\n"
    "The renamed '.locked_demo' files are harmless dummy files; use 'Reset demonstration' to restore them.\n"
)


class SandboxViolation(Exception):
    """Raised when something tries to touch a path outside the canonical sandbox."""


def canonical_norm(path: Path | str) -> str:
    """Resolve symlinks and normalize path casing for safe cross-platform / Windows comparison."""
    return os.path.normcase(os.path.realpath(os.path.abspath(str(path))))


class SafeAttackSimulator:
    def __init__(self, sandbox_root=None, device_ids=None, files_per_device: int = 24):
        raw_root = Path(sandbox_root) if sandbox_root is not None else DEFAULT_SANDBOX_ROOT
        raw_root.mkdir(parents=True, exist_ok=True)
        # Canonicalize AFTER ensuring the directory exists so Windows drive casing & symlinks stabilize.
        self.root = Path(os.path.realpath(str(raw_root))).resolve()
        self._root_norm = canonical_norm(self.root)
        self.device_ids = list(device_ids) if device_ids is not None else ["CAM-01", "TEMP-01", "PLC-01", "GW-01"]
        self.files_per_device = files_per_device
        self.prepare()

    # ---- path safety -------------------------------------------------
    def _is_within(self, parent_norm: str, candidate_norm: str) -> bool:
        try:
            return os.path.commonpath([parent_norm, candidate_norm]) == parent_norm
        except ValueError:
            # Different drives on Windows (e.g., C:\ vs D:\)
            return False

    def _check(self, path, device_id: str | None = None) -> Path:
        raw_path = Path(path)
        cand_real = os.path.realpath(os.path.abspath(str(raw_path)))
        cand_norm = os.path.normcase(cand_real)

        if not self._is_within(self._root_norm, cand_norm):
            logger.warning(
                "SandboxViolation refused path outside root | root=%s | candidate=%s | device_id=%s",
                self.root,
                raw_path,
                device_id,
            )
            raise SandboxViolation(f"Path outside sandbox refused: {path}")

        if device_id is not None:
            if device_id not in self.device_ids:
                logger.warning(
                    "SandboxViolation unknown device | root=%s | candidate=%s | device_id=%s",
                    self.root,
                    raw_path,
                    device_id,
                )
                raise SandboxViolation(f"Unknown device id refused: {device_id!r}")
            dev_norm = canonical_norm(self.root / device_id)
            if not self._is_within(dev_norm, cand_norm):
                logger.warning(
                    "SandboxViolation path outside device dir | root=%s | device_dir=%s | candidate=%s | device_id=%s",
                    self.root,
                    self.root / device_id,
                    raw_path,
                    device_id,
                )
                raise SandboxViolation(f"Path outside allowed device directory refused: {path}")

        return Path(cand_real)

    def _device_dir(self, device_id: str) -> Path:
        if device_id not in self.device_ids:  # blocks '../x', absolute paths, unknown names
            logger.warning("SandboxViolation unknown device_id=%r | root=%s", device_id, self.root)
            raise SandboxViolation(f"Unknown device id refused: {device_id!r}")
        return self._check(self.root / device_id, device_id=device_id)

    def _file_name(self, i: int) -> str:
        return f"dummy_file_{i:03d}{DUMMY_SUFFIX}"

    def _content(self, device_id: str, i: int) -> str:
        return f"DUMMY DEMO DATA for {device_id}, file {i:03d}. Not real data.\n"

    # ---- lifecycle ---------------------------------------------------
    def prepare(self) -> None:
        """Create (or recreate) the dummy files for every device."""
        for dev in self.device_ids:
            d = self._device_dir(dev)
            d.mkdir(parents=True, exist_ok=True)
            for i in range(self.files_per_device):
                f = self._check(d / self._file_name(i), device_id=dev)
                locked_f = self._check(d / (self._file_name(i) + LOCK_SUFFIX), device_id=dev)
                if not f.exists() and not locked_f.exists():
                    f.write_text(self._content(dev, i), encoding="utf-8")

    def reset(self) -> None:
        """Remove only files this simulator creates (dummy, locked, note) inside the sandbox, then recreate."""
        for dev in self.device_ids:
            d = self._device_dir(dev)
            if d.exists():
                for f in list(d.iterdir()):
                    f = self._check(f, device_id=dev)
                    if f.is_file() and (
                        f.name.endswith(DUMMY_SUFFIX)
                        or f.name.endswith(LOCK_SUFFIX)
                        or f.name == NOTE_NAME
                    ):
                        for attempt in range(5):
                            try:
                                f.unlink(missing_ok=True)
                                break
                            except (PermissionError, OSError):
                                if attempt == 4:
                                    raise
                                time.sleep(0.05)
        self.prepare()

    # ---- harmless "attack" step ---------------------------------------
    def advance(self, device_id: str, n_files: int = 3) -> dict:
        """Rename up to n_files dummy files of one device to '.locked_demo' (after appending a plain marker)."""
        d = self._device_dir(device_id)
        done = 0
        for f in sorted(d.glob(f"*{DUMMY_SUFFIX}")):
            if done >= n_files:
                break
            f = self._check(f, device_id=device_id)
            if not f.exists():
                continue
            with open(f, "a", encoding="utf-8") as fh:  # plain-text marker: a "file write" event, NOT encryption
                fh.write("[SIMULATED MODIFICATION]\n")
            target_file = self._check(f.with_name(f.name + LOCK_SUFFIX), device_id=device_id)
            # Robust file rename on Windows against momentary OS / AV scanner lock
            for attempt in range(5):
                try:
                    f.replace(target_file)
                    break
                except (PermissionError, OSError):
                    if attempt == 4:
                        raise
                    time.sleep(0.05)
            done += 1
        if done or any(d.glob(f"*{LOCK_SUFFIX}")):
            note = self._check(d / NOTE_NAME, device_id=device_id)
            if not note.exists():
                note.write_text(NOTE_TEXT, encoding="utf-8")
        return dict(device_id=device_id, renamed_now=done, **self.status(device_id))

    def status(self, device_id: str) -> dict:
        d = self._device_dir(device_id)
        return dict(
            dummy_files=len(list(d.glob(f"*{DUMMY_SUFFIX}"))),
            locked_demo_files=len(list(d.glob(f"*{LOCK_SUFFIX}"))),
            note_present=(d / NOTE_NAME).exists(),
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=BANNER)
    ap.add_argument("--target", default="PLC-01")
    ap.add_argument("--sandbox", default=str(DEFAULT_SANDBOX_ROOT))
    ap.add_argument("--reset", action="store_true", help="only reset the dummy files and exit")
    a = ap.parse_args()
    ids = ["CAM-01", "TEMP-01", "PLC-01", "GW-01"]
    sim = SafeAttackSimulator(a.sandbox, ids)
    print(BANNER)
    if a.reset:
        sim.reset()
        print("Sandbox reset: dummy files recreated.")
        return
    print(f"Target (virtual device): {a.target}  Sandbox: {sim.root}")
    while sim.status(a.target)["dummy_files"]:
        r = sim.advance(a.target, 6)
        print(f"  renamed {r['renamed_now']} dummy files -> total locked_demo: {r['locked_demo_files']}")
    print(f"Ransom note written: {sim.root / a.target / NOTE_NAME}")
    print("Done. Run with --reset to restore the dummy files.")


if __name__ == "__main__":
    main()
