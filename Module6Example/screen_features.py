"""Turn an asu_ndsu_screen_plays clip into the same 52 columns as pnr_windows.csv.

pnr_windows.csv was built from SkillCorner tracking of Spanish pro games (Liga ACB).
These clips were tracked off an ESPN+ broadcast of Arkansas State vs NDSU.
To run a model trained on one against the other, the columns have to mean
the same thing. This file does the translation; it does not do any modeling.

    from screen_features import load_clip, load_all_clips
    clip = load_clip("data/asu_ndsu_screen_plays/p1_10m32-10m07_astate_ndsu.csv")

What it matches from the ACB build:
  - court origin at center court, in feet   (ACB: center origin; here 0..94 x 0..50, so shift)
  - ball handler = the player nearest the ball, either team
  - teammates and defenders sorted nearest to farthest from the ball handler
  - half-second lookback for the movement columns   (ACB 12 frames @ 25fps; here 15 @ 30fps)

What it cannot match exactly:
  - speed. SkillCorner gives a speed; this data does not. Here speed is
    distance moved over the last half second, times 2 (feet per second).
    On the ACB data that same calculation lands within ~6% of their speed.
  - ball position. A held ball here sits on the holder's spot, so ball_dx/dy are 0.

game_clock assumes the clock ran for the whole clip. It is within about a second on four
clips and about 4 s off on the 11:08 clip, which starts in a dead ball. Use frame to find
a moment in the video; it matches the frame number printed on the .mp4.
"""
from pathlib import Path

import numpy as np
import pandas as pd

LOOKBACK = 15          # frames = 0.5 s at 30 fps
FPS = 30

FEATURES = (["bh_x", "bh_y", "bh_speed", "ball_dx", "ball_dy", "bh_dx_05s", "bh_dy_05s"]
            + [f"mate{i}_{s}" for i in range(1, 5) for s in ("dx", "dy", "speed", "relvx", "relvy")]
            + [f"def{i}_{s}" for i in range(1, 6) for s in ("dx", "dy", "speed", "relvx", "relvy")])


def _clock_start(clip_name):
    """'p1_10m32-10m07_astate_ndsu' -> 632 seconds left in the half at frame 1."""
    start = clip_name.split("_")[1].split("-")[0]          # '10m32'
    m, s = start.split("m")
    return int(m) * 60 + int(s)


def load_clip(csv_path):
    """One row per frame where all ten players and the ball are on the court."""
    csv_path = Path(csv_path)
    raw = pd.read_csv(csv_path)
    on_court = raw[raw.x_ft.notna()].copy()
    on_court["x"] = on_court.x_ft - 47
    on_court["y"] = on_court.y_ft - 25

    players = {f: g.set_index("player_id")
               for f, g in on_court[on_court.object == "player"].groupby("frame")}
    ball = on_court[on_court.object == "ball"].drop_duplicates("frame").set_index("frame")

    clock0 = _clock_start(csv_path.stem)
    rows = []
    for frame, g in players.items():
        if len(g) != 10 or g.team.value_counts().tolist() != [5, 5] or frame not in ball.index:
            continue
        prev = players.get(frame - LOOKBACK)
        if prev is None:
            continue

        bx, by = ball.loc[frame, "x"], ball.loc[frame, "y"]
        dist_to_ball = np.hypot(g.x - bx, g.y - by)
        bh_id = dist_to_ball.idxmin()
        bh = g.loc[bh_id]

        def moved(pid):
            # a player not seen half a second ago counts as not having moved (same as the ACB build)
            if pid not in prev.index:
                return 0.0, 0.0
            return g.loc[pid, "x"] - prev.loc[pid, "x"], g.loc[pid, "y"] - prev.loc[pid, "y"]

        bh_mx, bh_my = moved(bh_id)
        feats = [bh.x, bh.y, 2 * np.hypot(bh_mx, bh_my), bx - bh.x, by - bh.y, bh_mx, bh_my]

        others = g.drop(bh_id).assign(d=lambda o: np.hypot(o.x - bh.x, o.y - bh.y))
        mates = others[others.team == bh.team].sort_values("d")
        defs = others[others.team != bh.team].sort_values("d")
        for pid, p in pd.concat([mates, defs]).iterrows():
            mx, my = moved(pid)
            feats += [p.x - bh.x, p.y - bh.y, 2 * np.hypot(mx, my), mx - bh_mx, my - bh_my]

        t = (frame - 1) / FPS
        left = clock0 - t
        rows.append([csv_path.stem, frame, round(t, 3), f"{int(left // 60)}:{left % 60:04.1f}",
                     bh_id, bh.team] + feats)

    cols = ["clip", "frame", "t_clip_s", "game_clock", "bh_id", "bh_team"] + FEATURES
    return pd.DataFrame(rows, columns=cols)


def load_all_clips(folder="data/asu_ndsu_screen_plays"):
    return pd.concat([load_clip(p) for p in sorted(Path(folder).glob("*.csv"))],
                     ignore_index=True)


if __name__ == "__main__":
    df = load_all_clips()
    print(df.groupby("clip").size())
    print(df.shape)
