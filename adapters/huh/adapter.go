package main

import (
	"fmt"
	"io"
	"strings"

	"charm.land/bubbles/v2/cursor"
	tea "charm.land/bubbletea/v2"
	"charm.land/huh/v2"
)

type adapter struct {
	form          *huh.Form
	first, second string
}

// drain executes the real navigation/validation commands. Cursor ticks are allowed
// to finish but are not fed back, so periodic blinking cannot keep replay alive.
func (a *adapter) drain(cmd tea.Cmd, budget *int) error {
	if cmd == nil {
		return nil
	}
	*budget--
	if *budget < 0 {
		return fmt.Errorf("command limit exceeded")
	}
	switch msg := cmd().(type) {
	case nil, cursor.BlinkMsg, tea.QuitMsg:
		return nil
	case tea.BatchMsg:
		for _, child := range msg {
			if err := a.drain(child, budget); err != nil {
				return err
			}
		}
		return nil
	default:
		_, next := a.form.Update(msg)
		return a.drain(next, budget)
	}
}

func (a *adapter) send(msg tea.Msg) error {
	_, cmd := a.form.Update(msg)
	budget := 128
	return a.drain(cmd, &budget)
}

// step uses a real two-field form; bound values intentionally remain live on abort.
func (a *adapter) step(e event) (any, error) {
	if e.Op == "new" {
		if a.form != nil {
			return nil, fmt.Errorf("new is only allowed once")
		}
		if e.Width < 10 || e.Width > 1000 {
			return nil, fmt.Errorf("width must be 10..1000")
		}
		required := func(value string) error {
			if strings.TrimSpace(value) == "" {
				return fmt.Errorf("required")
			}
			return nil
		}
		a.form = huh.NewForm(huh.NewGroup(
			huh.NewInput().Key("first").Title("First").Value(&a.first).Validate(required),
			huh.NewInput().Key("second").Title("Second").Value(&a.second).Validate(required),
		)).WithWidth(e.Width).WithInput(nil).WithOutput(io.Discard).WithAccessible(false)
		// Init synchronously focuses the first field. The returned sequence requests
		// terminal size/blinking; explicit WindowSizeMsg replaces terminal discovery.
		a.form.Init()
		if err := a.send(tea.WindowSizeMsg{Width: e.Width, Height: 20}); err != nil {
			return nil, err
		}
	} else {
		if a.form == nil {
			return nil, fmt.Errorf("first event must be new")
		}
		switch e.Op {
		case "text":
			if err := a.send(tea.KeyPressMsg{Text: e.Text}); err != nil {
				return nil, err
			}
		case "key":
			key, err := keyMessage(e.Key)
			if err != nil {
				return nil, err
			}
			if err = a.send(key); err != nil {
				return nil, err
			}
		default:
			return nil, fmt.Errorf("unsupported op %q", e.Op)
		}
	}
	_ = a.form.View()
	state := "normal"
	if a.form.State == huh.StateCompleted {
		state = "completed"
	}
	if a.form.State == huh.StateAborted {
		state = "aborted"
	}
	focused, validation := "", ""
	if field := a.form.GetFocusedField(); field != nil {
		focused = field.GetKey()
		if err := field.Error(); err != nil {
			validation = err.Error()
		}
	}
	return struct {
		First      string `json:"first"`
		Second     string `json:"second"`
		Focused    string `json:"focused"`
		State      string `json:"status"`
		Validation string `json:"validation"`
	}{a.first, a.second, focused, state, validation}, nil
}
