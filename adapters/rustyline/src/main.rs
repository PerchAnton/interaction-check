#[path = "../../text_events.rs"]
mod events;
#[path = "../../widget_protocol.rs"]
mod protocol;
use events::{Event, bounded};
use rustyline::line_buffer::{ChangeListener, DeleteListener, Direction, LineBuffer};
use serde_json::json;
#[derive(Default)]
struct Observer {
    changes: usize,
    deleted: Vec<String>,
}
impl DeleteListener for Observer {
    fn delete(&mut self, _index: usize, value: &str, _direction: Direction) {
        self.changes += 1;
        self.deleted.push(value.to_owned());
    }
}
impl ChangeListener for Observer {
    fn insert_char(&mut self, _index: usize, _value: char) {
        self.changes += 1;
    }
    fn insert_str(&mut self, _index: usize, _value: &str) {
        self.changes += 1;
    }
    fn replace(&mut self, _index: usize, _old: &str, _new: &str) {
        self.changes += 1;
    }
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut model: Option<LineBuffer> = None;
    let mut observer = Observer::default();
    protocol::serve(move |event| {
        if let Event::New { text } = event {
            bounded(&text, 0)?;
            let mut buffer = LineBuffer::with_capacity(16384);
            buffer.update(&text, text.len(), &mut observer);
            observer = Observer::default();
            model = Some(buffer);
        } else {
            let buffer = model.as_mut().ok_or("first event must be new")?;
            match event {
                Event::Text { text } => {
                    bounded(&text, buffer.len())?;
                    buffer.yank(&text, 1, &mut observer);
                }
                Event::Key { key } => match key.as_str() {
                    "left" => {
                        buffer.move_backward(1);
                    }
                    "right" => {
                        buffer.move_forward(1);
                    }
                    "home" => {
                        buffer.move_home();
                    }
                    "end" => {
                        buffer.move_end();
                    }
                    "start" => {
                        buffer.move_buffer_start();
                    }
                    "finish" => {
                        buffer.move_buffer_end();
                    }
                    "backspace" => {
                        buffer.backspace(1, &mut observer);
                    }
                    "delete" => {
                        buffer.delete(1, &mut observer);
                    }
                    "transpose" => {
                        buffer.transpose_chars(&mut observer);
                    }
                    _ => return Err("unsupported key".into()),
                },
                Event::New { .. } => return Err("unexpected new event".into()),
            }
        }
        let buffer = model.as_ref().ok_or("missing buffer")?;
        Ok(
            json!({"value": buffer.as_str(), "cursor_bytes": buffer.pos(),
                  "changes": observer.changes, "deleted": observer.deleted}),
        )
    })
}
