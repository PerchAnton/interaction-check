package main

import (
	"fmt"

	"charm.land/bubbles/v2/textinput"
	tea "charm.land/bubbletea/v2"
)

type adapter struct {
	model textinput.Model
	ready bool
}

// step sends text and keys to the real Model.Update; expectations are never inputs.
func (a *adapter) step(e event) (any, error) {
	if e.Op == "new" {
		if a.ready {
			return nil, fmt.Errorf("new is only allowed once")
		}
		if e.Width < 1 || e.Width > 1000 {
			return nil, fmt.Errorf("width must be 1..1000")
		}
		a.model = textinput.New()
		a.model.SetVirtualCursor(false)
		a.model.SetWidth(e.Width)
		a.model.SetValue(e.Text)
		a.model.Focus() // Blink commands do not affect semantic state.
		a.ready = true
	} else {
		if !a.ready {
			return nil, fmt.Errorf("first event must be new")
		}
		switch e.Op {
		case "text":
			a.model, _ = a.model.Update(tea.KeyPressMsg{Text: e.Text})
		case "key":
			key, err := keyMessage(e.Key)
			if err != nil {
				return nil, err
			}
			a.model, _ = a.model.Update(key)
		case "resize":
			if e.Width < 1 || e.Width > 1000 {
				return nil, fmt.Errorf("width must be 1..1000")
			}
			a.model.SetWidth(e.Width)
		case "cursor":
			if e.Position < 0 {
				return nil, fmt.Errorf("cursor must be nonnegative")
			}
			a.model.SetCursor(e.Position)
		case "focus":
			a.model.Focus()
		case "blur":
			a.model.Blur()
		default:
			return nil, fmt.Errorf("unsupported op %q", e.Op)
		}
	}
	_ = a.model.View() // Exercise native layout, without asserting terminal escape sequences.
	return struct {
		Value    string `json:"value"`
		Position int    `json:"position_runes"`
		Focused  bool   `json:"focused"`
		Width    int    `json:"width"`
	}{a.model.Value(), a.model.Position(), a.model.Focused(), a.model.Width()}, nil
}
