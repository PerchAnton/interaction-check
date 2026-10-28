use helix_core::{
    Rope, Selection, Transaction,
    history::{History, State},
};
use pilot_protocol::{Result, bounded_text, serve};
use serde::Deserialize;
use serde_json::{Value, json};

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New { text: String },
    Replace { from: usize, to: usize, text: String },
    Undo {},
    Redo {},
}
struct Model {
    doc: Rope,
    history: History,
}
impl Model {
    fn state(&self) -> Value {
        json!({"text":self.doc.to_string(),"revision":self.history.current_revision(),"at_root":self.history.at_root()})
    }
    fn step(&mut self, event: Event) -> Result<Value> {
        match event {
            Event::Replace { from, to, text } => {
                bounded_text(&text)?;
                if from > to || to > self.doc.len_chars() || self.doc.len_chars() - (to - from) + text.chars().count() > 16384 {
                    return Err("invalid replacement bounds".into());
                }
                let original = State { doc: self.doc.clone(), selection: Selection::point(from) };
                let change = Transaction::change(&self.doc, std::iter::once((from, to, Some(text.into()))));
                if !change.apply(&mut self.doc) {
                    return Err("native transaction rejected".into());
                }
                self.history.commit_revision(&change, &original);
            }
            Event::Undo {} | Event::Redo {} => {
                let change = if matches!(event, Event::Undo {}) { self.history.undo() } else { self.history.redo() };
                if let Some(change) = change {
                    if !change.apply(&mut self.doc) {
                        return Err("native history rejected".into());
                    }
                }
            }
            Event::New { .. } => return Err("new handled by driver".into()),
        }
        Ok(self.state())
    }
}
fn main() -> Result<()> {
    let mut model = None::<Model>;
    serve(move |event| {
        if let Event::New { text } = event {
            bounded_text(&text)?;
            model = Some(Model { doc: Rope::from_str(&text), history: History::default() });
            return Ok(model.as_ref().ok_or("new failed")?.state());
        }
        model.as_mut().ok_or("new must be first")?.step(event)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn unicode_transaction_inverts_without_adapter() {
        let mut doc = Rope::from_str("aλ🦀b");
        let change = Transaction::change(&doc, std::iter::once((1, 3, Some("é".into()))));
        let inverse = change.invert(&doc);
        assert!(change.apply(&mut doc));
        assert_eq!(doc.to_string(), "aéb");
        assert!(inverse.apply(&mut doc));
        assert_eq!(doc.to_string(), "aλ🦀b");
    }
    #[test]
    fn bad_ranges_do_not_reach_native_api() {
        let mut model = Model { doc: Rope::from_str("a"), history: History::default() };
        assert!(model.step(Event::Replace { from: 2, to: 1, text: "x".into() }).is_err());
        assert_eq!(model.doc.to_string(), "a");
    }
}
