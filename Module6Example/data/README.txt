SCREEN PLAYS -- Arkansas State vs NDSU, 1st half

Five clips you picked by game clock, tracked by courtvision. Each play has a .mp4 (the broadcast
with the tracking drawn on it, beside the top-down court) and a .csv (the x/y data behind it).
Video and CSV frames are 1..N and match the source clips in ../ frame for frame.

file                               asked for                 frames  court  10 players  ball
p1_11m08-10m53_astate_ndsu.mp4     10:56 (whole live clip,      540    60%         36%   72%
p1_10m32-10m07_astate_ndsu.mp4     10:32 -> 10:07               767    98%         82%   75%
p1_07m22-06m58_astate_ndsu.mp4     7:22 -> 6:58                 750    91%         62%  100%
p1_05m41-05m16_astate_ndsu.mp4     5:41 -> 5:16                 780    93%         57%   96%
p1_02m33-02m08_astate_ndsu.mp4     2:33 -> 2:08                 782    93%         73%   81%

  court       share of frames with a court fit, so x/y feet are filled in
  10 players  share of frames where all ten players are placed on the court
  ball        share of frames with a ball row

Pipeline names (the clip each was tracked as, whole seconds of the game video):
  p1_11m08-10m53_astate_ndsu = astate_ndsu_19m39s-19m57s, frames 1-540 of that clip
  p1_10m32-10m07_astate_ndsu = astate_ndsu_20m32s-20m59s, frames 30-796 of that clip
  p1_07m22-06m58_astate_ndsu = astate_ndsu_29m05s-29m31s, frames 10-759 of that clip
  p1_05m41-05m16_astate_ndsu = astate_ndsu_33m21s-33m48s, frames 17-796 of that clip
  p1_02m33-02m08_astate_ndsu = astate_ndsu_40m04s-40m31s, frames 26-807 of that clip

----------------------------------------------------------------------
courtvision clip export -- 2026-09-17

Per clip:
  <clip>.mp4  the broadcast with the tracked result drawn on it, beside the top-down court, 30 fps
  <clip>.csv  the x/y data behind the video, one row per player or ball per frame

How players are identified (track_clip.py)
  Every person is followed frame to frame (BoT-SORT on a pose model). The jersey number is read
  with OCR on every frame it faces the camera; a track's number is the vote of all its reads,
  against the numbers in this game's box score, with reads off the back of the shirt (the big
  number) trusted over the front. Where a track's number stops reading and another track with
  that number starts, the first is cut there (the tracker swapped people). An unnumbered track
  is joined to a same-team player that ended just before it started, near where it starts, when
  it is the only one that fits, or when the other four teammates are on the floor beside it.
  Two OCR readers are used: EasyOCR on every frame, and RapidOCR only on the back-facing frames
  of tracks EasyOCR could not settle (it reads the white kit's thin "13" where EasyOCR cannot).
  Gaps inside one player of up to 2 s are filled by a straight line between the frames either
  side. Frames with no court fit of their own get the camera followed frame to frame on the
  floor's texture, forward from the last fit and backward from the next, blended. Nobody is
  followed outside the lines: a player hidden or off the court is simply absent until seen again.
  A player whose number was never read is "unknown a", "unknown b"... (player_id w?a, g?b in the CSV).

Cut clips (the rest of the file is another camera shot)
  astate_ndsu_20m32s-20m59s: the shot is clip frames 30-796 of 796; exported as frames 1-767
  astate_ndsu_29m05s-29m31s: the shot is clip frames 10-759 of 759; exported as frames 1-750
  astate_ndsu_33m21s-33m48s: the shot is clip frames 17-796 of 796; exported as frames 1-780
  astate_ndsu_40m04s-40m31s: the shot is clip frames 26-807 of 807; exported as frames 1-782


CSV columns
  frame              1-based, as on the video and the review page ("frame N of M")
  t_clip_s           seconds into the clip; game_video_time is the time in the full game video
  court              fit (this frame's own verified court fit); tracked (no fit of its own: the camera
                     was followed frame to frame on the floor's texture from the fits either side);
                     interpolated / held (older fallbacks); or none. Only frames with a court have x_ft/y_ft
  object             player or ball
  player_id          stable across the clip: w<jersey> / g<jersey> (white = A-State, green = NDSU),
                     or w?n / g?n for a player whose number was never read
  jersey, name       the jersey number and the box-score name; blank when never read
  jersey_source      read      the number was read off this stretch of the track
                     linked    this stretch never showed a readable number; it was joined to the
                               numbered player by position/time or by elimination
  position_source    detected  the player was detected in this frame, feet visible
                     estimated detected, feet hidden: standing point estimated from the body
                     filled    not detected: a straight line between the frames either side
  x_ft, y_ft         court feet: x 0..94 baseline to baseline, y 0..50 with 0 = camera-side sideline
  px_x, px_y         pixels in the 1280x720 broadcast: a player's standing point, the ball's centre
  ball_state         held      at the holding player's spot. Who holds it: of the players whose box the
                               ball is in, the one with a wrist nearest it. A man who holds it, is then
                               not seen with it for up to 4 s while the ball shows nowhere else, and holds
                               it again, held it throughout (ball_detected 0 on those frames)
                     in_air    on the straight line between the two players it went between
                     loose     the floor point under the ball -- approximate: a ball off the floor
                               lands too far from the camera
                     no_court  seen in the picture, but the frame has no court
  ball_held_by       the player_id of the holder in that frame
  ball_detected      1 = detected in this frame, 0 = filled in between detections or assumed (see held)
  per_frame_status   the older frame-by-frame check (pass / refused, and why): kept for reference,
                     it no longer decides what is plotted

Ball found on 19:39–19:57 clip 62% / 20:32–20:59 clip 55% / 29:05–29:30 clip 97% / 33:21–33:48 clip 89% / 40:04–40:31 clip 75% of frames. Frames with no ball row: not found.
