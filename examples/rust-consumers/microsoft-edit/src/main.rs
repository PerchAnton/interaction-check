use edit::buffer::TextBuffer;
use pilot_protocol::{Result, bounded_text, serve};
use serde::Deserialize;
use serde_json::{Value, json};

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Write { text: String },
    Move { offset: usize },
    MarkClean {},
    Undo {},
    Redo {},
}
fn fixture() -> Result<TextBuffer> {
    let mut b = TextBuffer::new(false)?;
    b.set_crlf(false);
    b.set_insert_final_newline(false);
    Ok(b)
}
fn text(b: &TextBuffer) -> Result<String> {
    let mut bytes = Vec::new();
    while bytes.len() < b.text_length() {
        let chunk = b.read_forward(bytes.len());
        if chunk.is_empty() {
            return Err("native read made no progress".into());
        }
        bytes.extend_from_slice(chunk);
    }
    Ok(String::from_utf8(bytes)?)
}
fn state(b: &TextBuffer) -> Result<Value> {
    Ok(json!({"text":text(b)?,"cursor":b.cursor_offset(),"dirty":b.is_dirty()}))
}
fn main() -> Result<()> {
    let mut model = None::<TextBuffer>;
    serve(move |event| {
        if matches!(event, Event::New {}) {
            model = Some(fixture()?);
            return state(model.as_ref().ok_or("new failed")?);
        }
        let b = model.as_mut().ok_or("new must be first")?;
        match event {
            Event::Write { text } => {
                bounded_text(&text)?;
                if b.text_length() + text.len() > 65536 {
                    return Err("buffer limit exceeded".into());
                }
                b.write_raw(text.as_bytes());
            }
            Event::Move { offset } => {
                if offset > b.text_length() || !text(b)?.is_char_boundary(offset) {
                    return Err("invalid byte offset".into());
                }
                b.cursor_move_to_offset(offset);
            }
            Event::MarkClean {} => b.mark_as_clean(),
            Event::Undo {} => b.undo(),
            Event::Redo {} => b.redo(),
            Event::New {} => return Err("new handled by driver".into()),
        }
        state(b)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_unicode_undo_redo() {
        let mut b = fixture().unwrap();
        b.write_raw("λ🦀".as_bytes());
        assert_eq!(text(&b).unwrap(), "λ🦀");
        b.undo();
        assert_eq!(text(&b).unwrap(), "");
        b.redo();
        assert_eq!(text(&b).unwrap(), "λ🦀");
    }
    #[test]
    fn reject_expect_injection() {
        assert!(serde_json::from_str::<Event>(r#"{"op":"undo","expect":{}}"#).is_err());
    }
}
