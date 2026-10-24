//! Headless adapter using PhotoCraft's real Session and command dispatch.
//! The separate edit-session Git dependency owns only the uncommitted parameter draft.
use edit_session::{EditSession, FinishError};
use photocraft_doc::{Color, ColorMode, DocId, Document, Layer, LayerId, SampleType, Size};
use photocraft_engine::{DocState, Session};
use serde_json::{Value, json};
use std::io::{self, BufRead, Write};

#[derive(PartialEq, Eq)]
struct Stamp(DocId, LayerId, u64);

struct Probe {
    session: Session,
    other: LayerId,
    draft: Option<EditSession<f32, Stamp>>,
}

impl Probe {
    fn new() -> Result<Self, String> {
        let mut doc = Document::with_background(
            "Synthetic probe",
            Size::new(8, 8),
            ColorMode::Rgb,
            SampleType::U8,
            Color::WHITE,
        );
        // Use ordinary raster layers so the opacity command does not also need to convert
        // a Background into a normal layer. That conversion belongs to PhotoCraft.
        let target = doc.insert_above(None, Layer::raster("Draft target", doc.pixel_format()));
        let other = doc.insert_above(None, Layer::raster("Other target", doc.pixel_format()));
        let mut session = Session::new();
        session.add_document(doc, None);
        session.select_layer(target).map_err(|e| e.to_string())?;
        Ok(Self {
            session,
            other,
            draft: None,
        })
    }

    fn active(&self) -> Result<&DocState, String> {
        self.session.active().ok_or_else(|| "no document".into())
    }

    fn target(&self) -> Result<LayerId, String> {
        self.active()?
            .active_layer
            .ok_or_else(|| "no target".into())
    }

    fn stamp(&self) -> Result<Stamp, String> {
        let state = self.active()?;
        Ok(Stamp(state.doc.id, self.target()?, state.revision))
    }

    fn value(&self) -> Result<f32, String> {
        self.active()?
            .doc
            .layer(self.target()?)
            .map(|layer| layer.opacity)
            .ok_or_else(|| "target is gone".into())
    }

    fn apply(&mut self, opacity: f32) -> Result<(), String> {
        self.session
            .execute(
                "layer.setProps",
                json!({"layer": self.target()?.0, "opacity": opacity}),
            )
            .map_err(|e| e.to_string())?;
        Ok(())
    }

    fn run(&mut self, event: &Value) -> Result<(), String> {
        match event
            .get("op")
            .and_then(Value::as_str)
            .ok_or("missing op")?
        {
            "begin" => {
                if self.draft.is_some() {
                    return Err("already editing".into());
                }
                self.draft = Some(EditSession::new(self.value()?, self.stamp()?));
            }
            "preview" => {
                let proposal = valid_opacity(event);
                self.draft.as_mut().ok_or("no draft")?.propose(proposal)?;
            }
            "commit" => {
                let live = self.value()?;
                let stamp = self.stamp()?;
                let check = self.draft.as_ref().ok_or("no draft")?.check(&live, &stamp);
                if let Err(error) = check {
                    if error != FinishError::InvalidProposal {
                        self.draft = None;
                    }
                    return Err(finish_error(error).into());
                }
                let draft = self.draft.take().ok_or("no draft")?;
                if let Some(change) = draft.finish(&live, &stamp).map_err(finish_error)? {
                    self.apply(change.after)?;
                }
            }
            "cancel" => {
                self.draft.take().ok_or("no draft")?.cancel();
            }
            "external" => {
                self.apply(valid_opacity(event)?)?;
            }
            "select-other" => {
                let previous = self.target()?;
                self.session
                    .select_layer(self.other)
                    .map_err(|e| e.to_string())?;
                self.other = previous;
            }
            "undo" | "redo" => {
                if event["op"] == "undo" {
                    self.session.undo();
                } else {
                    self.session.redo();
                }
            }
            "inspect" => {}
            _ => return Err("unknown op".into()),
        }
        Ok(())
    }

    fn state(&self, error: Option<String>) -> Value {
        json!({
            "committed": self.value().ok(),
            "preview": self.draft.as_ref().map(|d| *d.preview()),
            "editing": self.draft.is_some(),
            "valid": self.draft.as_ref().is_none_or(EditSession::is_valid),
            "undo_depth": self.active().ok().map(|s| s.history.past_len()),
            "can_redo": self.active().ok().map(|s| s.history.can_redo()),
            "revision": self.active().ok().map(|s| s.revision),
            "command_count": self.session.journal.len(),
            "error": error
        })
    }
}

fn valid_opacity(event: &Value) -> Result<f32, String> {
    let value = event
        .get("value")
        .and_then(Value::as_f64)
        .ok_or("invalid opacity")?;
    if !value.is_finite() || !(0.0..=1.0).contains(&value) {
        return Err("invalid opacity".into());
    }
    Ok(value as f32)
}

fn finish_error(error: FinishError) -> &'static str {
    match error {
        FinishError::InvalidProposal => "invalid proposal",
        FinishError::ContextChanged => "context changed",
        FinishError::ValueChanged => "value changed",
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut probe = Probe::new()?;
    let mut stdout = io::stdout().lock();
    for line in io::stdin().lock().lines() {
        let request: Value = serde_json::from_str(&line?)?;
        if request["protocol"] != 1
            || request.get("id").and_then(Value::as_u64).is_none()
            || !request["event"].is_object()
        {
            return Err("invalid protocol envelope".into());
        }
        let error = probe.run(&request["event"]).err();
        let response = json!({"protocol": 1, "id": request["id"], "state": probe.state(error)});
        writeln!(stdout, "{response}")?;
        stdout.flush()?;
    }
    Ok(())
}
