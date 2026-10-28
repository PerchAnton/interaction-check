// Compiled inside Amp's existing cfg(test) library, using its own TestTerminal.
use crate::{commands, input::Key, models::Application};
use pilot_protocol::{bounded_text, serve, Result};
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Event {
    New {},
    Type { text: String },
    Undo {},
    Redo {},
    Backspace {},
    Home {},
}

fn fixture() -> Result<Application> {
    let mut app = Application::new(&[]).map_err(|e| e.to_string())?;
    app.workspace.add_buffer(scribe::Buffer::new());
    Ok(app)
}

fn state(app: &Application) -> Result<Value> {
    let buffer = app.workspace.current_buffer.as_ref().ok_or("missing buffer")?;
    Ok(json!({"text":buffer.data(), "line":buffer.cursor.line, "offset":buffer.cursor.offset}))
}

fn step(app: &mut Application, event: Event) -> Result<Value> {
    match event {
        Event::Type { text } => {
            bounded_text(&text)?;
            let size = app.workspace.current_buffer.as_ref().ok_or("missing buffer")?.data().len();
            if size + text.len() > 65536 {
                return Err("buffer limit exceeded".into());
            }
            if text.contains(['\n', '\r']) {
                return Err("single-line fixture only".into());
            }
            for character in text.chars() {
                app.view.last_key = Some(Key::Char(character));
                commands::buffer::insert_char(app).map_err(|e| e.to_string())?;
            }
        }
        Event::Undo {} => commands::buffer::undo(app).map_err(|e| e.to_string())?,
        Event::Redo {} => commands::buffer::redo(app).map_err(|e| e.to_string())?,
        Event::Backspace {} => commands::buffer::backspace(app).map_err(|e| e.to_string())?,
        Event::Home {} => commands::cursor::move_to_start_of_line(app).map_err(|e| e.to_string())?,
        Event::New {} => return Err("new handled by driver".into()),
    }
    state(app)
}

#[test]
#[ignore = "JSONL test bridge; invoked only by the external adapter"]
fn replay() {
    let mut app = None::<Application>;
    serve(move |event| {
        if matches!(event, Event::New {}) {
            app = Some(fixture()?);
            return state(app.as_ref().ok_or("new failed")?);
        }
        step(app.as_mut().ok_or("new must be first")?, event)
    })
    .unwrap();
}

#[test]
fn native_unicode_history() {
    let mut app = fixture().unwrap();
    app.view.last_key = Some(Key::Char('λ'));
    commands::buffer::insert_char(&mut app).unwrap();
    assert_eq!(app.workspace.current_buffer.as_ref().unwrap().data(), "λ");
    commands::buffer::undo(&mut app).unwrap();
    assert_eq!(app.workspace.current_buffer.as_ref().unwrap().data(), "");
    commands::buffer::redo(&mut app).unwrap();
    assert_eq!(app.workspace.current_buffer.as_ref().unwrap().data(), "λ");
}
