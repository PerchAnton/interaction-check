#[path = "../../text_events.rs"]
mod events;
#[path = "../../widget_protocol.rs"]
mod protocol;
use events::{Event, bounded};
use rat_text::text_input::TextInputState;
use serde_json::json;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut model: Option<TextInputState> = None;
    let mut group_open = false;
    protocol::serve(move |event| {
        if let Event::New { text } = event {
            bounded(&text, 0)?;
            let mut buffer = TextInputState::new();
            buffer.set_text(text);
            buffer.move_to_line_end(false);
            model = Some(buffer);
            group_open = false;
        } else {
            let buffer = model.as_mut().ok_or("first event must be new")?;
            match event {
                Event::Text { text } => {
                    bounded(&text, buffer.len_bytes())?;
                    buffer.insert_str(text);
                }
                Event::Key { key } => match key.as_str() {
                    "left" => {
                        buffer.move_left(false);
                    }
                    "right" => {
                        buffer.move_right(false);
                    }
                    "home" => {
                        buffer.move_to_line_start(false);
                    }
                    "end" => {
                        buffer.move_to_line_end(false);
                    }
                    "backspace" => {
                        buffer.delete_prev_char();
                    }
                    "delete" => {
                        buffer.delete_next_char();
                    }
                    "undo" => {
                        buffer.undo();
                    }
                    "redo" => {
                        buffer.redo();
                    }
                    "select_all" => {
                        buffer.select_all();
                    }
                    "begin_group" if !group_open => {
                        buffer
                            .undo_buffer_mut()
                            .ok_or("missing undo buffer")?
                            .begin_seq();
                        group_open = true;
                    }
                    "end_group" if group_open => {
                        buffer
                            .undo_buffer_mut()
                            .ok_or("missing undo buffer")?
                            .end_seq();
                        group_open = false;
                    }
                    _ => return Err("unsupported key".into()),
                },
                Event::New { .. } => return Err("unexpected new event".into()),
            }
        }
        let buffer = model.as_ref().ok_or("missing buffer")?;
        Ok(
            json!({"value": buffer.text(), "cursor_graphemes": buffer.cursor(),
                  "selection": [buffer.selection().start, buffer.selection().end]}),
        )
    })
}
