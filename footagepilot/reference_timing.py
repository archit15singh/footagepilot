"""Decoded frame timing and conservative audio pulse evidence for reference edits."""
from bisect import bisect_left
import re


def decoded_frames(log):
    """Read FFmpeg scdet metadata on a microsecond time base."""
    rows = []
    headers = re.compile(r'^frame:(\d+)\s+pts:\s*(-?\d+)\s+pts_time:', re.M)
    scores = re.compile(r'^lavfi\.scd\.(mafd|score)=([\d.]+)$', re.M)
    for number, ticks in headers.findall(log):
        rows.append({'index': int(number), 'time': int(ticks) / 1_000_000})
    measurements = scores.findall(log)
    if not rows or len(measurements) != 2 * len(rows):
        raise ValueError('Missing per-frame scene metadata')
    for i, row in enumerate(rows):
        mafd, score = measurements[2*i:2*i+2]
        if row['index'] != i or (mafd[0], score[0]) != ('mafd', 'score'):
            raise ValueError('Unexpected per-frame scene metadata order')
        row.update(change=float(mafd[1]), change_score=float(score[1]))
    if rows[0]['time'] < 0 or any(a['time'] >= b['time'] for a,b in zip(rows, rows[1:])):
        raise ValueError('Reference video timestamps must be nonnegative and increasing')
    return rows


def frame_selection(indices):
    """Build a shallow FFmpeg expression with logarithmic evaluation per frame."""
    if len(indices) == 1:
        return f'eq(n,{indices[0]})'
    middle = len(indices) // 2
    left = frame_selection(indices[:middle])
    right = frame_selection(indices[middle:])
    return f'if(lt(n,{indices[middle]}),{left},{right})'


def nearest(times, time):
    i = bisect_left(times, time)
    return min(times[max(0,i-1):i+1], key=lambda t: abs(t-time), default=None)


def estimate_pulse(events):
    """Fit a constant-period grid to repeated transients, with minimum coverage."""
    times = [event['time'] for event in events]
    if len(times) < 6 or times[-1] - times[0] < 2:
        return {'status': 'inconclusive', 'times': []}
    best_by_period = {}
    for ticks in range(30, 91):
        period = ticks / 100
        for anchor in times[:12]:
            first = anchor - ((anchor - times[0]) // period) * period
            grid = [first + i*period for i in range(-1, int((times[-1]-first)/period)+2)]
            grid = [t for t in grid if times[0]-.045 <= t <= times[-1]+.045]
            hits = [t for t in grid if abs(nearest(times, t)-t) <= .045]
            if len(hits) >= 6 and len(hits) >= .75*len(grid) and len(hits) >= .55*len(times):
                residual = sum(abs(nearest(times, t)-t) for t in hits)/len(hits)
                quality = 2*len(hits)/(len(grid)+len(times)) - residual
                if period not in best_by_period or quality > best_by_period[period][0]:
                    best_by_period[period] = (quality, period, grid, hits)
    if not best_by_period:
        return {'status': 'inconclusive', 'times': []}
    candidates = best_by_period.values()
    quality, period, grid, hits = max(candidates, key=lambda row: row[0])
    # Competing periods with comparable support make the rate ambiguous.
    if any(abs(other-period) > .05 and score >= quality-.035 for score,other,_,_ in candidates):
        return {'status': 'inconclusive', 'times': []}
    return {'status': 'estimated', 'period_seconds': period, 'bpm': round(60/period, 1),
            'matched_pulses': len(hits),
            'times': [round(t, 3) for t in grid if max(0,hits[0]) <= t <= hits[-1]]}


def transition_timing(cuts, frames, onsets, pulse):
    frame_times = [row['time'] for row in frames]
    onset_times = [row['time'] for row in onsets]
    pulse_times = pulse['times']
    rows = []
    for cut in cuts:
        time = cut
        index = bisect_left(frame_times, time)
        if index == len(frames) or frame_times[index] != time:
            raise ValueError('Scene candidate has no matching decoded frame')
        onset = nearest(onset_times, time)
        pulse_time = nearest(pulse_times, time) if pulse_times and pulse_times[0]-.08 <= time <= pulse_times[-1]+.08 else None
        rows.append({'time': time, 'frame_index': index, 'change_score': frames[index]['change_score'],
                     'nearest_onset': onset, 'cut_minus_onset_seconds': round(time-onset, 6) if onset is not None else None,
                     'nearest_pulse': pulse_time, 'cut_minus_pulse_seconds': round(time-pulse_time, 6) if pulse_time is not None else None})
    return rows
