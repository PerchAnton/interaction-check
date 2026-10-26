use floem_reactive::{Effect, RwSignal, Scope, SignalGet, SignalUpdate};
use pilot_protocol::{Result, serve};
use serde::Deserialize;
use serde_json::{Value, json};
use std::{
    cell::{Cell, RefCell},
    rc::Rc,
};

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Set { left: i32, right: i32 },
    SetLeft { value: i32 },
    Choose { left: bool },
    Dispose {},
}

struct Model {
    scope: Scope,
    left: RwSignal<i32>,
    right: RwSignal<i32>,
    choose: RwSignal<bool>,
    observed: Rc<Cell<i32>>,
    runs: Rc<Cell<usize>>,
    disposed: bool,
}
impl Model {
    fn new() -> Self {
        let scope = Scope::new();
        let left = scope.create_rw_signal(1);
        let right = scope.create_rw_signal(2);
        let choose = scope.create_rw_signal(true);
        let observed = Rc::new(Cell::new(0));
        let runs = Rc::new(Cell::new(0));
        let value = observed.clone();
        let count = runs.clone();
        scope.create_effect(move |_| {
            value.set(if choose.get() { left.get() } else { right.get() });
            count.set(count.get() + 1);
        });
        Self { scope, left, right, choose, observed, runs, disposed: false }
    }
    fn step(&mut self, event: Event) -> Result<Value> {
        match event {
            Event::New {} => return Err("new handled by driver".into()),
            Event::Set { left, right } if !self.disposed => Effect::batch(|| {
                self.left.set(left);
                self.right.set(right);
            }),
            Event::SetLeft { value } if !self.disposed => self.left.set(value),
            Event::Choose { left } if !self.disposed => self.choose.set(left),
            Event::Dispose {} => {
                if !self.disposed {
                    self.scope.dispose();
                    self.disposed = true;
                }
            }
            _ => return Err("scope is disposed".into()),
        }
        Ok(self.state())
    }
    fn state(&self) -> Value {
        json!({"observed":self.observed.get(),"runs":self.runs.get(),"disposed":self.disposed})
    }
}
impl Drop for Model {
    fn drop(&mut self) {
        if !self.disposed {
            self.scope.dispose();
        }
    }
}
fn main() -> Result<()> {
    let model = RefCell::new(None::<Model>);
    serve(move |event| {
        let mut model = model.borrow_mut();
        if matches!(event, Event::New {}) {
            *model = Some(Model::new());
            return Ok(model.as_ref().ok_or("new failed")?.state());
        }
        model.as_mut().ok_or("new must be first")?.step(event)
    })
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn batch_and_dynamic_dependencies_are_native() {
        let model = Model::new();
        Effect::batch(|| {
            model.left.set(3);
            model.right.set(4);
        });
        assert_eq!((model.observed.get(), model.runs.get()), (3, 2));
        model.choose.set(false);
        model.left.set(5);
        assert_eq!((model.observed.get(), model.runs.get()), (4, 3));
    }
    #[test]
    fn reject_unknown_event_fields() {
        assert!(serde_json::from_str::<Event>(r#"{"op":"dispose","expect":{}}"#).is_err());
    }
}
