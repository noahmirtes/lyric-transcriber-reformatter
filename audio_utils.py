import numpy as np
import soundfile as sf

EPS = 1e-12

def db_to_linear(db):
    return 10.0 ** (db / 20.0)

def linear_to_db(x):
    return 20.0 * np.log10(np.maximum(x, EPS))

def smoothing_coefficient(time_seconds, sample_rate):
    """
    Returns coefficient for a one-pole smoothing filter:
        coeff = exp(-1 / (tau * Fs))
    Used for attack/release envelopes etc.
    """
    tau = max(time_seconds, 1e-9)
    return np.exp(-1.0 / (tau * sample_rate))


def load_audio(path : str):
    with open(path, 'r') as f:
        x, sr = sf.read(f)
        return x, sr

# -------------------------------------------- #

def peak_normalize(audio: np.ndarray, target_peak: float = 0.999) -> np.ndarray:
    """Normalize audio so its peak is at target_peak. """

    # Find absolute peak
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio  # Avoid division by zero (silent audio)

    # Compute scale factor
    scale = target_peak / peak

    # Apply scaling in place
    return audio * scale



def simple_gate(audio, sr, threshold_db=-35.0, attack_ms=10.0, release_ms=200.0):
    """
    audio: float32 array shaped (num_samples, 2), range [-1, 1]
    """

    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("audio must be stereo with shape (N, 2)")

    # Convert threshold to linear
    threshold = 10 ** (threshold_db / 20.0)

    # Attack / release coefficients
    attack_coeff = np.exp(-1.0 / (sr * attack_ms / 1000.0))
    release_coeff = np.exp(-1.0 / (sr * release_ms / 1000.0))

    env = 0.0
    gain = 0.0

    out = np.zeros_like(audio, dtype=np.float32)

    for n in range(audio.shape[0]):
        # --- LEVEL DETECTOR (linked stereo) ---
        # Average absolute magnitude of L and R
        mag = 0.5 * (abs(audio[n, 0]) + abs(audio[n, 1]))

        if mag > env:
            env = mag
        else:
            env = release_coeff * env + (1.0 - release_coeff) * mag

        # --- THRESHOLD DECISION ---
        target_gain = 1.0 if env >= threshold else 0.0

        # --- GAIN SMOOTHING ---
        if target_gain > gain:
            gain = attack_coeff * gain + (1.0 - attack_coeff) * target_gain
        else:
            gain = release_coeff * gain + (1.0 - release_coeff) * target_gain

        # --- APPLY SAME GAIN TO BOTH CHANNELS ---
        out[n, 0] = audio[n, 0] * gain
        out[n, 1] = audio[n, 1] * gain

    return out


def trim_silence_my_version(audio, sr, silence_threshold=-60, pad_ms=250, min_clip_len_sec=4.0):

    threshold = db_to_linear(silence_threshold)

    indices = []
    index_range = [None, None]

    min_clip_size = sr * min_clip_len_sec

    pad_samples = sr * (pad_ms / 1000)

    for n in range(audio.shape[0]):
        mag = (abs(audio[n, 0]) + abs(audio[n, 1])) / 2

        if mag > threshold and index_range[0] is None:
            index_range[0] = n
        elif mag < threshold and index_range[0] is not None:
            
            if (n - index_range[0]) < min_clip_size:
                index_range[0] = None
                continue

            index_range[1] = n
            indices.append(index_range)
            index_range = [None, None]


    print(indices)
    # cut at silent indices
    out_segments = []
    for rng in indices:
        start = rng[0]
        end = rng[1]

        #slice_start = int(max(0, start-pad_samples))
        #slice_end = int(min(audio.shape[0], end+pad_samples))

        slice_start = int(start-pad_samples)
        slice_end = int(end+pad_samples)

        print(slice_start, slice_end)

        out_segments.append(audio[slice_start:slice_end])


    print(len(out_segments))
    out = np.concatenate(out_segments)
    return out



def trim_silence(audio, sr, silence_threshold=-60, pad_ms=250, min_clip_len_sec=4.0):
    threshold = db_to_linear(silence_threshold)

    min_clip_size = int(sr * min_clip_len_sec)
    pad_samples = int(sr * (pad_ms / 1000.0))

    # hangover: allow short dips below threshold without closing the segment
    hangover_ms = 250
    hangover_samples = int(sr * (hangover_ms / 1000.0))

    indices = []
    start = None
    below_count = 0

    for n in range(audio.shape[0]):
        mag = (abs(audio[n, 0]) + abs(audio[n, 1])) * 0.5

        if mag >= threshold:
            if start is None:
                start = n
            below_count = 0
        else:
            if start is not None:
                below_count += 1
                if below_count >= hangover_samples:
                    end = n - below_count  # end at the start of the below-threshold run
                    if (end - start) >= min_clip_size:
                        indices.append((start, end))
                    start = None
                    below_count = 0

    # handle file ending while still inside a segment
    if start is not None:
        end = audio.shape[0] - below_count
        if (end - start) >= min_clip_size:
            indices.append((start, end))

    out_segments = []
    for start, end in indices:
        s = max(0, start - pad_samples)
        e = min(audio.shape[0], end + pad_samples)
        out_segments.append(audio[s:e])

    if not out_segments:
        return audio[:0]

    return np.concatenate(out_segments, axis=0)