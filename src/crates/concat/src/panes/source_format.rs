// SPDX-License-Identifier: AGPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Vuki contributors

/// Fit the first source within the engine limit while keeping its shape.
/// Even dimensions work with the default encoder. A photo has no frame rate.
pub(super) fn project_format(width: u32, height: u32, rate: Option<&str>) -> (u32, u32, i64, i64) {
    let scale = (8192.0 / width.max(height).max(1) as f64).min(1.0);
    let side = |value: u32| ((value as f64 * scale / 2.0).round() as u32 * 2).clamp(16, 8192);
    let fraction = rate
        .and_then(|rate| rate.split_once('/'))
        .and_then(|(n, d)| {
            let (n, d) = (n.parse::<i64>().ok()?, d.parse::<i64>().ok()?);
            (n > 0 && d > 0 && (1.0..=240.0).contains(&(n as f64 / d as f64))).then_some((n, d))
        });
    let (num, den) = fraction.unwrap_or((30, 1));
    (side(width), side(height), num, den)
}

#[cfg(test)]
mod tests {
    use super::project_format;
    #[test]
    fn portrait_landscape_and_square_keep_shape_and_exact_rate() {
        for (w, h) in [(1080, 1920), (1920, 1080), (1080, 1080)] {
            assert_eq!(
                project_format(w, h, Some("30000/1001")),
                (w, h, 30000, 1001)
            );
        }
    }
    #[test]
    fn photos_and_invalid_rates_use_a_safe_default() {
        assert_eq!(project_format(1200, 1600, None), (1200, 1600, 30, 1));
        for rate in ["0/0", "30/0", "unknown", "-30/1", "999/1"] {
            assert_eq!(project_format(1080, 1080, Some(rate)), (1080, 1080, 30, 1));
        }
    }
    #[test]
    fn oversized_sources_scale_both_sides_and_dimensions_are_even() {
        assert_eq!(project_format(16384, 9216, None), (8192, 4608, 30, 1));
        assert_eq!(project_format(1081, 1921, None), (1082, 1922, 30, 1));
        assert_eq!(project_format(0, 0, None), (16, 16, 30, 1));
    }
}
