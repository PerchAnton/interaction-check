use edit_session::EditSession;
use icy_engine_edit::{EditState, UndoState};
use pilot_protocol::{Result, bounded_text, serve};
use serde::Deserialize;
use serde_json::{Value, json};

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Open {},
    Propose { name: String },
    Cancel {},
    Confirm {},
    Direct { name: String },
    Undo {},
    Redo {},
}
type Draft = EditSession<String, (u64, usize, u64)>;
struct Model {
    host: EditState,
    draft: Option<Draft>,
    generation: u64,
    last: &'static str,
}
impl Model {
    fn new() -> Result<Self> {
        let mut host = EditState::default();
        host.get_buffer_mut().layers.get_mut(0).ok_or("missing fixture layer")?.properties.title = "original".into();
        Ok(Self { host, draft: None, generation: 0, last: "none" })
    }
    fn name(&self) -> Result<String> {
        Ok(self.host.get_buffer().layers.first().ok_or("target removed")?.properties.title.clone())
    }
    fn context(&self) -> (u64, usize, u64) {
        (1, 0, self.generation)
    }
    fn rename(&mut self, name: String) -> Result<()> {
        let mut properties = self.host.get_buffer().layers.first().ok_or("target removed")?.properties.clone();
        properties.title = name;
        self.host.update_layer_properties(0, properties)?;
        self.generation = self.generation.checked_add(1).ok_or("generation overflow")?;
        Ok(())
    }
    fn step(&mut self, event: Event) -> Result<Value> {
        match event {
            Event::Open {} => {
                self.draft = Some(EditSession::new(self.name()?, self.context()));
                self.last = "opened";
            }
            Event::Propose { name } => {
                bounded_text(&name)?;
                self.draft.as_mut().ok_or("open required")?.propose::<&str>(Ok(name)).map_err(|_| "invalid proposal")?;
                self.last = "proposed";
            }
            Event::Cancel {} => {
                self.draft = None;
                self.last = "cancelled";
            }
            Event::Confirm {} => {
                if let Some(draft) = self.draft.take() {
                    match draft.finish(&self.name()?, &self.context()) {
                        Ok(None) => self.last = "noop",
                        Ok(Some(change)) => {
                            self.rename(change.after)?;
                            self.last = "applied";
                        }
                        Err(_) => self.last = "stale",
                    }
                } else {
                    self.last = "closed";
                }
            }
            Event::Direct { name } => {
                bounded_text(&name)?;
                self.rename(name)?;
                self.last = "direct";
            }
            Event::Undo {} => {
                if self.host.can_undo() {
                    self.host.undo()?;
                    self.generation += 1;
                }
                self.last = "undo";
            }
            Event::Redo {} => {
                if self.host.can_redo() {
                    self.host.redo()?;
                    self.generation += 1;
                }
                self.last = "redo";
            }
            Event::New {} => return Err("new handled by driver".into()),
        }
        self.state()
    }
    fn state(&self) -> Result<Value> {
        Ok(json!({"name":self.name()?,"open":self.draft.is_some(),"undo":self.host.undo_stack_len(),"can_redo":self.host.can_redo(),"last":self.last}))
    }
}
fn main() -> Result<()> {
    let mut model = None::<Model>;
    serve(move |event| {
        if matches!(event, Event::New {}) {
            model = Some(Model::new()?);
            return model.as_ref().ok_or("new failed")?.state();
        }
        model.as_mut().ok_or("new must be first")?.step(event)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_property_command_undo_redo() {
        let mut m = Model::new().unwrap();
        m.rename("new".into()).unwrap();
        m.host.undo().unwrap();
        assert_eq!(m.name().unwrap(), "original");
        m.host.redo().unwrap();
        assert_eq!(m.name().unwrap(), "new");
    }
    #[test]
    fn checked_noop_preserves_native_redo() {
        let mut m = Model::new().unwrap();
        m.rename("new".into()).unwrap();
        m.step(Event::Undo {}).unwrap();
        m.step(Event::Open {}).unwrap();
        m.step(Event::Confirm {}).unwrap();
        assert!(m.host.can_redo());
        assert_eq!(m.host.undo_stack_len(), 0);
    }
}
