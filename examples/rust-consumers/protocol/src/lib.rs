use serde::Deserialize;
use serde::de::DeserializeOwned;
use serde_json::Value;
use std::io::{self, BufRead, Read, Write};

pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
const LIMIT: usize = 65536;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Packet<E> {
    protocol: u8,
    id: u64,
    event: E,
}

pub fn bounded_text(text: &str) -> Result<()> {
    if text.chars().count() > 4096 {
        return Err("text limit exceeded".into());
    }
    Ok(())
}

pub fn serve<E: DeserializeOwned>(mut step: impl FnMut(E) -> Result<Value>) -> Result<()> {
    let input = io::stdin();
    let mut input = input.lock();
    let output = io::stdout();
    let mut output = output.lock();
    let mut count = 0;
    loop {
        let mut line = Vec::new();
        let n = Read::by_ref(&mut input).take((LIMIT + 1) as u64).read_until(b'\n', &mut line)?;
        if n == 0 {
            break;
        }
        count += 1;
        if n > LIMIT || count > 1024 {
            return Err("request limit exceeded".into());
        }
        let request: Packet<E> = serde_json::from_slice(&line)?;
        if request.protocol != 1 || request.id > 9_007_199_254_740_991 {
            return Err("unsupported protocol or id".into());
        }
        let state = step(request.event)?;
        if !state.is_object() {
            return Err("expected state object".into());
        }
        let response = serde_json::to_vec(&serde_json::json!({"protocol":1,"id":request.id,"state":state}))?;
        if response.len() >= LIMIT {
            return Err("response limit exceeded".into());
        }
        output.write_all(&response)?;
        output.write_all(b"\n")?;
        output.flush()?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn reject_duplicate_fields_and_non_integer_ids() {
        for data in [r#"{"protocol":1,"id":1,"id":2,"event":{}}"#, r#"{"protocol":1,"id":true,"event":{}}"#, r#"{"protocol":1,"id":1,"event":{},"expect":{}}"#]
        {
            assert!(serde_json::from_str::<Packet<Value>>(data).is_err());
        }
    }
    #[test]
    fn enforce_text_limit_in_characters() {
        assert!(bounded_text(&"λ".repeat(4096)).is_ok());
        assert!(bounded_text(&"λ".repeat(4097)).is_err());
    }
}
