#[path = "../../text_events.rs"]
mod events;
#[path = "../../widget_protocol.rs"]
mod protocol;
use events::{Event, bounded};
use reedline::LineBuffer;
use serde_json::json;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut model: Option<LineBuffer> = None;
    protocol::serve(move |event| {
        if let Event::New { text } = event {
            bounded(&text, 0)?;
            let mut buffer = LineBuffer::new();
            buffer.set_buffer(text);
            buffer.move_to_end();
            model = Some(buffer);
        } else {
            let buffer = model.as_mut().ok_or("first event must be new")?;
            match event {
                Event::Text { text } => {
                    bounded(&text, buffer.len())?;
                    buffer.insert_str(&text);
                }
                Event::Key { key } => match key.as_str() {
                    "left" => buffer.move_left(),
                    "right" => buffer.move_right(),
                    "home" => buffer.move_to_line_start(),
                    "end" => buffer.move_to_line_end(),
                    "start" => buffer.move_to_start(),
                    "finish" => buffer.move_to_end(),
                    "backspace" => buffer.delete_left_grapheme(),
                    "delete" => buffer.delete_right_grapheme(),
                    _ => return Err("unsupported key".into()),
                },
                Event::New { .. } => return Err("unexpected new event".into()),
            }
        }
        let buffer = model.as_ref().ok_or("missing buffer")?;
        Ok(
            json!({"value": buffer.get_buffer(), "cursor_bytes": buffer.insertion_point(),
                  "valid": buffer.is_valid(), "lines": buffer.num_lines()}),
        )
    })
}
