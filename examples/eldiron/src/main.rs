use pilot_protocol::{Result, bounded_text, serve};
use serde::Deserialize;
use serde_json::{Value, json};
use theframework::prelude::*;

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Paste { text: String },
    Set { text: String },
    Undo {},
    Redo {},
}
struct Model {
    input: TheTextLineEdit,
    context: TheContext,
}
impl Model {
    fn new() -> Self {
        let mut input = TheTextLineEdit::new(TheId::named("Replay Name"));
        input.set_value(TheValue::Text(String::new()));
        Self { input, context: TheContext::new(320, 100, 1.0) }
    }
    fn text(&self) -> Result<String> {
        self.input.value().to_string().ok_or_else(|| "expected text value".into())
    }
    fn step(&mut self, event: Event) -> Result<Value> {
        match event {
            Event::Paste { text } => {
                bounded_text(&text)?;
                if self.text()?.len() + text.len() > 65536 {
                    return Err("text limit exceeded".into());
                }
                self.input.on_event(&TheEvent::Paste(TheValue::Text(text), None), &mut self.context);
            }
            Event::Set { text } => {
                bounded_text(&text)?;
                self.input.set_value(TheValue::Text(text));
            }
            Event::Undo {} => {
                self.input.on_event(&TheEvent::Undo, &mut self.context);
            }
            Event::Redo {} => {
                self.input.on_event(&TheEvent::Redo, &mut self.context);
            }
            Event::New {} => return Err("new handled by driver".into()),
        }
        self.state()
    }
    fn state(&self) -> Result<Value> {
        Ok(json!({"text":self.text()?}))
    }
}
fn main() -> Result<()> {
    let mut model = None::<Model>;
    serve(move |event| {
        if matches!(event, Event::New {}) {
            model = Some(Model::new());
            return model.as_ref().ok_or("new failed")?.state();
        }
        model.as_mut().ok_or("new must be first")?.step(event)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_widget_paste_undo_redo() {
        let mut m = Model::new();
        m.input.on_event(&TheEvent::Paste(TheValue::Text("λ🦀".into()), None), &mut m.context);
        assert_eq!(m.text().unwrap(), "λ🦀");
        m.input.on_event(&TheEvent::Undo, &mut m.context);
        assert_eq!(m.text().unwrap(), "");
        m.input.on_event(&TheEvent::Redo, &mut m.context);
        assert_eq!(m.text().unwrap(), "λ🦀");
    }
    #[test]
    fn reject_unknown_event_fields() {
        assert!(serde_json::from_str::<Event>(r#"{"op":"undo","expect":{}}"#).is_err());
    }
}
