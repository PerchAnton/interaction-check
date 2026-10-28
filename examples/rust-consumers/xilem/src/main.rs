use pilot_protocol::{Result, serve};
use serde::Deserialize;
use serde_json::{Value, json};
use xilem_core::{
    AppendVec, DynMessage, ElementSplice, Environment, MessageCtx, MessageResult, Mut, NoElement, View, ViewId, ViewMarker, ViewPathTracker, ViewSequence,
};

#[derive(Default)]
struct Data {
    accepted: usize,
    builds: usize,
}
struct Context {
    environment: Environment,
    path: Vec<ViewId>,
    last_path: Vec<ViewId>,
    teardowns: usize,
}
impl Default for Context {
    fn default() -> Self {
        Self { environment: Environment::new(), path: vec![], last_path: vec![], teardowns: 0 }
    }
}
impl ViewPathTracker for Context {
    fn environment(&mut self) -> &mut Environment {
        &mut self.environment
    }
    fn push_id(&mut self, id: ViewId) {
        self.path.push(id);
    }
    fn pop_id(&mut self) {
        self.path.pop();
    }
    fn view_path(&mut self) -> &[ViewId] {
        &self.path
    }
}
// An original no-element fixture. Option<ViewSequence> owns generation routing.
#[derive(Clone, Copy)]
struct Pulse;
impl ViewMarker for Pulse {}
impl View<Data, (), Context> for Pulse {
    type Element = NoElement;
    type ViewState = ();
    fn build(&self, ctx: &mut Context, data: &mut Data) -> (NoElement, ()) {
        data.builds += 1;
        ctx.last_path = ctx.path.clone();
        (NoElement, ())
    }
    fn rebuild(&self, _: &Self, _: &mut (), _: &mut Context, _: Mut<'_, NoElement>, _: &mut Data) {}
    fn teardown(&self, _: &mut (), ctx: &mut Context, _: Mut<'_, NoElement>) {
        ctx.teardowns += 1;
    }
    fn message(&self, _: &mut (), ctx: &mut MessageCtx, _: Mut<'_, NoElement>, data: &mut Data) -> MessageResult<()> {
        if ctx.take_message::<u32>().is_some() {
            data.accepted += 1;
            MessageResult::Action(())
        } else {
            MessageResult::Stale
        }
    }
}
// A no-element fixture has no rendering allocation to mutate.
struct Empty;
impl ElementSplice<NoElement> for Empty {
    fn with_scratch<R>(&mut self, f: impl FnOnce(&mut AppendVec<NoElement>) -> R) -> R {
        f(&mut AppendVec::default())
    }
    fn insert(&mut self, _: NoElement) {}
    fn mutate<R>(&mut self, f: impl FnOnce(()) -> R) -> R {
        f(())
    }
    fn skip(&mut self, _: usize) {}
    fn index(&self) -> usize {
        0
    }
    fn delete<R>(&mut self, f: impl FnOnce(()) -> R) -> R {
        f(())
    }
}
type Sequence = Option<Pulse>;
type SequenceState = <Sequence as ViewSequence<Data, (), Context, NoElement>>::SeqState;
struct Model {
    view: Sequence,
    state: SequenceState,
    context: Context,
    data: Data,
    saved: Vec<ViewId>,
    last: &'static str,
}
impl Model {
    fn new() -> Self {
        let view = Some(Pulse);
        let mut context = Context::default();
        let mut data = Data::default();
        let state = view.seq_build(&mut context, &mut AppendVec::<NoElement>::default(), &mut data);
        let saved = context.last_path.clone();
        Self { view, state, context, data, saved, last: "none" }
    }
    fn show(&mut self, present: bool) {
        let next = present.then_some(Pulse);
        next.seq_rebuild(&self.view, &mut self.state, &mut self.context, &mut Empty, &mut self.data);
        self.view = next;
    }
    fn send(&mut self, saved: bool) {
        let path = if saved { self.saved.clone() } else { self.context.last_path.clone() };
        let mut context = MessageCtx::new(std::mem::replace(&mut self.context.environment, Environment::new()), path, DynMessage::new(7_u32));
        self.last = match self.view.seq_message(&mut self.state, &mut context, &mut Empty, &mut self.data) {
            MessageResult::Action(()) => "accepted",
            MessageResult::Stale => "stale",
            _ => "other",
        };
        self.context.environment = context.finish().0;
    }
    fn state(&self) -> Value {
        json!({"present":self.view.is_some(),"builds":self.data.builds,"teardowns":self.context.teardowns,"accepted":self.data.accepted,"last":self.last})
    }
}
#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Show { present: bool },
    SavePath {},
    Send { saved: bool },
}
fn main() -> Result<()> {
    let mut model = None::<Model>;
    serve(move |event| {
        if matches!(event, Event::New {}) {
            model = Some(Model::new());
            return Ok(model.as_ref().ok_or("new failed")?.state());
        }
        let m = model.as_mut().ok_or("new must be first")?;
        match event {
            Event::Show { present } => m.show(present),
            Event::SavePath {} => m.saved = m.context.last_path.clone(),
            Event::Send { saved } => m.send(saved),
            Event::New {} => return Err("new handled by driver".into()),
        }
        Ok(m.state())
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn option_generation_rejects_previous_incarnation() {
        let mut m = Model::new();
        m.show(false);
        m.show(true);
        m.send(true);
        assert_eq!(m.last, "stale");
        assert_eq!(m.data.accepted, 0);
        m.send(false);
        assert_eq!(m.data.accepted, 1);
    }
    #[test]
    fn unchanged_presence_does_not_rebuild_child() {
        let mut m = Model::new();
        m.show(true);
        assert_eq!(m.data.builds, 1);
        m.show(false);
        m.show(false);
        assert_eq!(m.context.teardowns, 1);
    }
}
