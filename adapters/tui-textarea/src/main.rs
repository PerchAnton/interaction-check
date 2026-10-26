use serde::Deserialize;
use serde_json::json;
use tui_textarea::{Input, Key, TextArea};
#[path = "../../widget_protocol.rs"]
mod protocol;

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New { lines: Vec<String> },
    Text { text: String },
    Key { key: String },
    SelectAll,
    Delete { chars: Option<usize> },
}

fn main() {
    let mut model: Option<TextArea<'static>> = None;
    let result = protocol::serve(|event| {
        let mut changed = false;
        match event {
            Event::New { lines } => {
                if model.is_some() {
                    return Err("new is only allowed once".into());
                }
                model = Some(TextArea::new(lines));
            }
            event => {
                let area = model.as_mut().ok_or("first event must be new")?;
                match event {
                    Event::Text { text } => {
                        for c in text.chars() {
                            changed |= area.input(Input {
                                key: Key::Char(c),
                                ..Input::default()
                            });
                        }
                    }
                    Event::Key { key } => {
                        let (key, ctrl) = match key.as_str() {
                            "left" => (Key::Left, false),
                            "right" => (Key::Right, false),
                            "home" => (Key::Home, false),
                            "end" => (Key::End, false),
                            "up" => (Key::Up, false),
                            "down" => (Key::Down, false),
                            "backspace" => (Key::Backspace, false),
                            "delete" => (Key::Delete, false),
                            "enter" => (Key::Enter, false),
                            "undo" => (Key::Char('u'), true),
                            "redo" => (Key::Char('r'), true),
                            _ => return Err(format!("unsupported key {key}")),
                        };
                        changed = area.input(Input {
                            key,
                            ctrl,
                            ..Input::default()
                        });
                    }
                    Event::SelectAll => area.select_all(),
                    Event::Delete { chars } => {
                        changed = area.delete_str(chars.unwrap_or(usize::MAX))
                    }
                    Event::New { .. } => return Err("unexpected new".into()),
                }
            }
        }
        let area = model.as_ref().ok_or("model unavailable")?;
        Ok(
            json!({"lines":area.lines(),"cursor":area.cursor(),"selection":area.selection_range(),"changed":changed}),
        )
    });
    if let Err(err) = result {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
