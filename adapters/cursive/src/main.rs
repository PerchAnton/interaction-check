//! JSONL adapter for Cursive's actual EditView and callback dispatch.
use cursive_core::{
    Cursive, Vec2,
    event::{Event, Key},
    view::View,
    views::EditView,
};
use serde::Deserialize;
use serde_json::json;
use std::io::{self, BufRead, Read, Write};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Request {
    protocol: u8,
    id: u64,
    event: Input,
}

#[derive(Deserialize)]
#[serde(tag = "op", rename_all = "snake_case", deny_unknown_fields)]
enum Input {
    New {
        width: usize,
        #[serde(default)]
        text: String,
    },
    Text {
        text: String,
    },
    Key {
        key: String,
    },
    Resize {
        width: usize,
    },
    Cursor {
        position: usize,
    },
}

#[derive(Default)]
struct Submitted {
    values: Vec<String>,
}

struct Adapter {
    view: EditView,
    siv: Cursive,
    width: usize,
}

impl Adapter {
    fn new(width: usize, text: String) -> Self {
        let mut siv = Cursive::new();
        siv.set_user_data(Submitted::default());
        let mut view = EditView::new().content(text);
        view.set_on_submit(|s, text| {
            if let Some(submitted) = s.user_data::<Submitted>() {
                submitted.values.push(text.to_owned());
            }
        });
        Self { view, siv, width }
    }

    /// Dispatch through View, then process the callback as the Cursive event loop does.
    fn send(&mut self, event: Event) {
        self.view.on_event(event).process(&mut self.siv);
    }

    fn step(&mut self, input: Input) -> Result<(), String> {
        match input {
            Input::New { .. } => return Err("new is only allowed once".into()),
            Input::Text { text } => {
                for c in text.chars() {
                    self.send(Event::Char(c));
                }
            }
            Input::Key { key } => {
                let event = match key.as_str() {
                    "left" => Event::Key(Key::Left),
                    "right" => Event::Key(Key::Right),
                    "home" => Event::Key(Key::Home),
                    "end" => Event::Key(Key::End),
                    "backspace" => Event::Key(Key::Backspace),
                    "delete" => Event::Key(Key::Del),
                    "enter" => Event::Key(Key::Enter),
                    "escape" => Event::Key(Key::Esc),
                    "ctrl+a" => Event::CtrlChar('a'),
                    "ctrl+e" => Event::CtrlChar('e'),
                    _ => return Err(format!("unsupported key {key:?}")),
                };
                self.send(event);
            }
            Input::Resize { width } => {
                check_width(width)?;
                self.width = width;
            }
            Input::Cursor { position } => {
                if !self.view.get_content().is_char_boundary(position) {
                    return Err("cursor must be an in-range UTF-8 byte boundary".into());
                }
                self.view.set_cursor(position);
            }
        }
        self.view.layout(Vec2::new(self.width, 1));
        Ok(())
    }

    fn state(&mut self) -> serde_json::Value {
        let submitted = self
            .siv
            .user_data::<Submitted>()
            .map(|s| s.values.clone())
            .unwrap_or_default();
        json!({"value": self.view.get_content().as_str(), "position_bytes": self.view.get_cursor(),
            "width": self.width, "submitted": submitted})
    }
}

fn check_width(width: usize) -> Result<(), String> {
    if (1..=1000).contains(&width) {
        Ok(())
    } else {
        Err("width must be 1..1000".into())
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut input = io::stdin().lock();
    let mut output = io::stdout().lock();
    let mut adapter: Option<Adapter> = None;
    loop {
        let mut line = Vec::new();
        if Read::by_ref(&mut input)
            .take(65537)
            .read_until(b'\n', &mut line)?
            == 0
        {
            break;
        }
        if line.len() > 65536 {
            return Err("request exceeds 64 KiB".into());
        }
        let req: Request = serde_json::from_slice(&line)?;
        if req.protocol != 1 {
            return Err("unsupported protocol".into());
        }
        match (&mut adapter, req.event) {
            (None, Input::New { width, text }) => {
                check_width(width)?;
                let mut model = Adapter::new(width, text);
                model.view.layout(Vec2::new(width, 1));
                adapter = Some(model);
            }
            (Some(model), event) => model.step(event)?,
            (None, _) => return Err("first event must be new".into()),
        }
        if let Some(model) = &mut adapter {
            serde_json::to_writer(
                &mut output,
                &json!({"protocol":1,"id":req.id,"state":model.state()}),
            )?;
            writeln!(output)?;
        }
    }
    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
