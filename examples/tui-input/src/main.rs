use serde::Deserialize;
use serde_json::json;
use tui_input::{Input, InputRequest};
mod protocol;

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New { text: String, width: usize },
    Text { text: String },
    Key { key: String },
    Resize { width: usize },
}

fn main() {
    let mut model: Option<Input> = None;
    let mut width = 1;
    let result = protocol::serve(|event| {
        match event {
            Event::New { text, width: w } => {
                if model.is_some() {
                    return Err("new is only allowed once".into());
                }
                if !(1..=1000).contains(&w) {
                    return Err("width must be 1..1000".into());
                }
                model = Some(Input::new(text));
                width = w;
            }
            event => {
                let input = model.as_mut().ok_or("first event must be new")?;
                match event {
                    Event::Text { text } => {
                        for c in text.chars() {
                            input.handle(InputRequest::InsertChar(c));
                        }
                    }
                    Event::Key { key } => {
                        let req = match key.as_str() {
                            "left" => InputRequest::GoToPrevChar,
                            "right" => InputRequest::GoToNextChar,
                            "home" => InputRequest::GoToStart,
                            "end" => InputRequest::GoToEnd,
                            "backspace" => InputRequest::DeletePrevChar,
                            "delete" => InputRequest::DeleteNextChar,
                            "ctrl+w" => InputRequest::DeletePrevWord,
                            "ctrl+k" => InputRequest::DeleteTillEnd,
                            "ctrl+y" => InputRequest::Yank,
                            _ => return Err(format!("unsupported key {key}")),
                        };
                        input.handle(req);
                    }
                    Event::Resize { width: w } => {
                        if !(1..=1000).contains(&w) {
                            return Err("width must be 1..1000".into());
                        }
                        width = w;
                    }
                    Event::New { .. } => return Err("unexpected new".into()),
                }
            }
        }
        let input = model.as_ref().ok_or("model unavailable")?;
        Ok(
            json!({"value":input.value(),"position_codepoints":input.cursor(),
            "visual_cursor":input.visual_cursor(),"scroll_columns":input.visual_scroll(width),"width":width}),
        )
    });
    if let Err(err) = result {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
