import pytest

from src.safe_attack_simulator import BANNER, LOCK_SUFFIX, NOTE_NAME, SafeAttackSimulator, SandboxViolation

IDS = ["CAM-01", "TEMP-01", "PLC-01", "GW-01"]


@pytest.fixture()
def sim(tmp_path):
    return SafeAttackSimulator(tmp_path / "demo_sandbox", IDS, files_per_device=10)


def test_creates_dummy_files_only_in_sandbox(sim, tmp_path):
    assert sim.status("PLC-01")["dummy_files"] == 10
    assert {p.name for p in tmp_path.iterdir()} == {"demo_sandbox"}


def test_attack_renames_and_writes_note_without_encryption(sim):
    r = sim.advance("PLC-01", 4)
    assert r["renamed_now"] == 4 and r["locked_demo_files"] == 4 and r["note_present"]
    locked = sorted((sim.root / "PLC-01").glob(f"*{LOCK_SUFFIX}"))[0]
    text = locked.read_text(encoding="utf-8")
    assert text.startswith("DUMMY DEMO DATA")             # still readable plain text: nothing encrypted
    note = (sim.root / "PLC-01" / NOTE_NAME).read_text(encoding="utf-8")
    assert BANNER in note and "SIMULATED" in note
    assert sim.status("CAM-01")["locked_demo_files"] == 0  # only the target is touched


def test_path_restrictions(sim, tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("keep me", encoding="utf-8")
    for bad in ("../outside", "..", "/etc", "PLC-02", ""):
        with pytest.raises(SandboxViolation):
            sim.advance(bad)
    with pytest.raises(SandboxViolation):
        sim._check(outside)
    with pytest.raises(SandboxViolation):
        sim._check(sim.root / ".." / "outside.txt")
    assert outside.read_text(encoding="utf-8") == "keep me"


def test_reset_restores_and_leaves_foreign_files(sim):
    foreign = sim.root / "PLC-01" / "my_real_notes.docx"
    foreign.write_text("personal", encoding="utf-8")
    sim.advance("PLC-01", 10)
    assert sim.status("PLC-01")["dummy_files"] == 0
    sim.reset()
    st = sim.status("PLC-01")
    assert st["dummy_files"] == 10 and st["locked_demo_files"] == 0 and not st["note_present"]
    assert foreign.read_text(encoding="utf-8") == "personal"                # reset only removes files this simulator created
    assert (sim.root / "PLC-01" / "dummy_file_000.demo").read_text(encoding="utf-8").startswith("DUMMY DEMO DATA")


def test_symlink_escape_is_refused(sim, tmp_path):
    target = tmp_path / "elsewhere"
    target.mkdir()
    link = sim.root / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(SandboxViolation):
        sim._check(link / "x.txt")


def test_windows_path_casing_and_device_isolation(sim):
    """Valid paths with mixed Windows casing must pass; cross-device paths must fail."""
    cam_file = sim.root / "CAM-01" / "dummy_file_000.demo"
    # Mixed case representation (relevant on case-insensitive Windows filesystems)
    mixed = str(cam_file)
    if len(mixed) > 2 and mixed[1] == ":":
        swapped = (mixed[0].lower() if mixed[0].isupper() else mixed[0].upper()) + mixed[1:]
        assert sim._check(swapped, device_id="CAM-01").name == "dummy_file_000.demo"
    # Cross-device access must be refused
    with pytest.raises(SandboxViolation):
        sim._check(cam_file, device_id="PLC-01")