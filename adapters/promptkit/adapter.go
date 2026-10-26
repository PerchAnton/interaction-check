package main

import (
	tea "charm.land/bubbletea/v2"
	"errors"
	"fmt"
	"github.com/erikgeiser/promptkit"
	"github.com/erikgeiser/promptkit/textinput"
	"github.com/muesli/termenv"
)

type adapter struct {
	model     *textinput.Model
	submitted bool
}

func (a *adapter) close() {}

// step drives the real text prompt model; timer commands are not scheduled.
func (a *adapter) step(e event) (any, error) {
	if len(e.Text) > 4096 {
		return nil, fmt.Errorf("text too large")
	}
	if e.Op == "new" {
		if e.CharLimit < 0 || e.CharLimit > 4096 {
			return nil, fmt.Errorf("invalid char limit")
		}
		p := textinput.New("Value:")
		p.InitialValue = e.Text
		p.CharLimit = e.CharLimit
		p.ColorProfile = termenv.Ascii
		if e.DigitsOnly {
			p.Validate = func(value string) error {
				if value == "" {
					return fmt.Errorf("digits required")
				}
				for _, ch := range value {
					if ch < '0' || ch > '9' {
						return fmt.Errorf("digits required")
					}
				}
				return nil
			}
		}
		a.model = textinput.NewModel(p)
		a.model.Init()
		a.submitted = false
	} else if a.model == nil {
		return nil, fmt.Errorf("first event must be new")
	} else {
		switch e.Op {
		case "text":
			for _, ch := range e.Text {
				a.model.Update(tea.KeyPressMsg{Code: ch, Text: string(ch)})
			}
		case "resize":
			if e.Width < 2 || e.Width > 200 {
				return nil, fmt.Errorf("invalid width")
			}
			a.model.Update(tea.WindowSizeMsg{Width: e.Width, Height: 10})
		case "key":
			keys := map[string]rune{"left": tea.KeyLeft, "right": tea.KeyRight, "home": tea.KeyHome, "end": tea.KeyEnd, "backspace": tea.KeyBackspace, "delete": tea.KeyDelete, "enter": tea.KeyEnter, "escape": tea.KeyEscape}
			if e.Key == "ctrl+c" {
				a.model.Update(tea.KeyPressMsg{Code: 'c', Mod: tea.ModCtrl})
				break
			}
			key, ok := keys[e.Key]
			if !ok {
				return nil, fmt.Errorf("unsupported key")
			}
			_, cmd := a.model.Update(tea.KeyPressMsg{Code: key})
			if e.Key == "enter" && cmd != nil {
				_, a.submitted = cmd().(tea.QuitMsg)
			}
		default:
			return nil, fmt.Errorf("unsupported event")
		}
	}
	value, err := a.model.Value()
	if err != nil && !errors.Is(err, promptkit.ErrAborted) {
		return nil, err
	}
	return map[string]any{"value": value, "submitted": a.submitted, "aborted": errors.Is(err, promptkit.ErrAborted), "view": a.model.View().Content}, nil
}
