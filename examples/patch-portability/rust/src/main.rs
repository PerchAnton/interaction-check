use serde_json::{Value, json};
use std::error::Error;
use std::io::{self, BufRead};

fn main() -> Result<(), Box<dyn Error>> {
    let mut document = Value::Null;
    for line in io::stdin().lock().lines() {
        let request: Value = serde_json::from_str(&line?)?;
        if request["protocol"] != 1 {
            return Err("invalid protocol".into());
        }
        let event = &request["event"];
        let mut error = Value::Null;
        match event["op"].as_str() {
            Some("new") => document = event["data"].clone(),
            Some("apply") => {
                let patch: json_patch::Patch = serde_json::from_value(event["patch"].clone())?;
                if json_patch::patch(&mut document, &patch).is_err() {
                    error = json!("rejected");
                }
            }
            Some("merge") => json_patch::merge(&mut document, &event["patch"]),
            _ => return Err("unknown event".into()),
        }
        println!(
            "{}",
            json!({"protocol":1,"id":request["id"],"state":{"document":document,"error":error}})
        );
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn failed_patch_is_atomic_without_an_extra_copy() -> Result<(), Box<dyn Error>> {
        let mut document = json!({"n":1});
        let patch: json_patch::Patch = serde_json::from_value(json!([
            {"op":"replace","path":"/n","value":2},
            {"op":"test","path":"/n","value":9}
        ]))?;
        assert!(json_patch::patch(&mut document, &patch).is_err());
        assert_eq!(document, json!({"n":1}));
        Ok(())
    }
}
