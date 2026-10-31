use tui_input::{Input, InputRequest};

#[test]
fn delete_one_grapheme() {
    let mut input = Input::new("xe\u{301}界".into());
    assert_eq!(
        (input.value(), input.cursor(), input.visual_cursor()),
        ("xe\u{301}界", 4, 4)
    );
    input.handle(InputRequest::GoToPrevChar);
    assert_eq!((input.cursor(), input.visual_cursor()), (3, 2));
    input.handle(InputRequest::GoToPrevChar);
    assert_eq!((input.cursor(), input.visual_cursor()), (1, 1));
    input.handle(InputRequest::DeleteNextChar);
    assert_eq!((input.value(), input.cursor()), ("x界", 1));
}
