//! Bounded JSONL transport shared by the external Rust widget probes.
use serde::{Deserialize, de::DeserializeOwned};
use serde_json::Value;
use std::io::{self, BufRead, Read, Write};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request<E> {
    protocol: u8,
    id: u64,
    event: E,
}

pub fn serve<E: DeserializeOwned>(
    mut step: impl FnMut(E) -> Result<Value, String>,
) -> Result<(), Box<dyn std::error::Error>> {
    let mut input = io::stdin().lock();
    let mut output = io::stdout().lock();
    loop {
        let mut line = Vec::new();
        if Read::by_ref(&mut input)
            .take(65537)
            .read_until(b'\n', &mut line)?
            == 0
        {
            break;
        }
        if line.len() > 65536 {
            return Err("request exceeds 64 KiB".into());
        }
        let req: Request<E> = serde_json::from_slice(&line)?;
        if req.protocol != 1 {
            return Err("unsupported protocol".into());
        }
        let state = step(req.event)?;
        serde_json::to_writer(
            &mut output,
            &serde_json::json!({"protocol":1,"id":req.id,"state":state}),
        )?;
        writeln!(output)?;
    }
    Ok(())
}
