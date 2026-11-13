"""Versioned, Resolve-native creative looks for SDR footage."""

PRESETS = {
    'soft-color-v1': {'label': 'FootagePilot Soft Color v1', 'saturation': 0.65},
    'monochrome-v1': {'label': 'FootagePilot Monochrome v1', 'saturation': 0.0},
}


def color_preset(data, backend='resolve'):
    if 'color_preset' not in data:
        return None
    name = data['color_preset']
    if not isinstance(name, str) or name not in PRESETS:
        raise ValueError('Unknown color_preset; choose ' + ', '.join(PRESETS))
    if backend != 'resolve':
        raise ValueError('Color presets require Resolve')
    return {'id': name, **PRESETS[name]}


def sdr_source(video):
    # Untagged footage is common. The preset is an explicit declaration that
    # untagged sources are SDR, never an automatic log/HDR conversion.
    for field, allowed in (
        ('color_transfer', {'bt709', 'iec61966-2-1', 'smpte170m', 'bt470bg'}),
        ('color_primaries', {'bt709', 'smpte170m', 'bt470bg'}),
        ('color_space', {'bt709', 'smpte170m', 'bt470bg', 'gbr'}),
    ):
        value = video.get(field)
        if value not in (None, 'unknown', 'unspecified') and value not in allowed:
            raise ValueError(f'Color preset requires SDR footage; {field} is {value}')


def apply_saturation(rgb, saturation):
    """Independent ASC CDL saturation model for rendered-frame QA."""
    result = []
    for i in range(0, len(rgb), 3):
        r, g, b = rgb[i:i+3]
        luma = 0.2126*r + 0.7152*g + 0.0722*b
        result.extend(luma + saturation*(value-luma) for value in (r, g, b))
    return result


def chroma(rgb, indices):
    """Channel differences isolate saturation from shared luminance errors."""
    values = []
    for i in indices:
        r, g, b = rgb[i:i+3]
        values.extend((r-g, b-g))
    return values
