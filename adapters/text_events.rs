//! Events for bounded, terminal-free native text buffer probes.
use serde::Deserialize;
#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
pub enum Event {
    New { text: String },
    Text { text: String },
    Key { key: String },
}
pub fn bounded(text: &str, existing: usize) -> Result<(), String> {
    if existing.saturating_add(text.len()) > 16384 {
        return Err("text exceeds 16 KiB".into());
    }
    Ok(())
}
