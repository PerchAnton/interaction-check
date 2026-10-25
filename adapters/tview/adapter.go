package main

import (
	"fmt"
	"strconv"
	"unicode"

	"github.com/gdamore/tcell/v2"
	"github.com/rivo/tview"
)

// adapter owns the native field and a memory-only terminal screen.
type adapter struct {
	field   *tview.InputField
	screen  tcell.SimulationScreen
	changes int
	done    []string
	width   int
}

// close releases the simulated screen without touching a user's terminal.
func (a *adapter) close() {
	if a.screen != nil {
		a.screen.Fini()
	}
}

// step routes keys through InputHandler and observes real changed/done callbacks.
func (a *adapter) step(e event) (any, error) {
	if e.Op == "new" {
		if a.field != nil {
			return nil, fmt.Errorf("new is only allowed once")
		}
		if e.Width < 1 || e.Width > 1000 {
			return nil, fmt.Errorf("width must be 1..1000")
		}
		a.width = e.Width
		a.screen = tcell.NewSimulationScreen("UTF-8")
		if err := a.screen.Init(); err != nil {
			return nil, err
		}
		a.screen.SetSize(a.width, 3)
		a.field = tview.NewInputField().SetText(e.Text)
		a.done = []string{}
		a.field.SetChangedFunc(func(string) { a.changes++ })
		a.field.SetDoneFunc(func(k tcell.Key) {
			name := map[tcell.Key]string{tcell.KeyEnter: "enter", tcell.KeyEscape: "escape", tcell.KeyTab: "tab", tcell.KeyBacktab: "shift+tab"}[k]
			if name == "" {
				name = strconv.Itoa(int(k))
			}
			a.done = append(a.done, name)
		})
		if e.DigitsOnly {
			a.field.SetAcceptanceFunc(func(value string, _ rune) bool {
				for _, r := range value {
					if !unicode.IsDigit(r) {
						return false
					}
				}
				return true
			})
		}
		a.field.Focus(func(tview.Primitive) {})
	} else {
		if a.field == nil {
			return nil, fmt.Errorf("first event must be new")
		}
		handler := a.field.InputHandler()
		switch e.Op {
		case "text":
			for _, r := range e.Text {
				handler(tcell.NewEventKey(tcell.KeyRune, r, tcell.ModNone), func(tview.Primitive) {})
			}
		case "key":
			k, err := keyMessage(e.Key)
			if err != nil {
				return nil, err
			}
			handler(k, func(tview.Primitive) {})
		case "resize":
			if e.Width < 1 || e.Width > 1000 {
				return nil, fmt.Errorf("width must be 1..1000")
			}
			a.width = e.Width
			a.screen.SetSize(a.width, 3)
		default:
			return nil, fmt.Errorf("unsupported op %q", e.Op)
		}
	}
	a.field.SetRect(0, 0, a.width, 1)
	a.screen.Clear()
	a.field.Draw(a.screen)
	a.screen.Show()
	x, y, visible := a.screen.GetCursor()
	return struct {
		Value         string   `json:"value"`
		Changes       int      `json:"changes"`
		Done          []string `json:"done"`
		Width         int      `json:"width"`
		CursorX       int      `json:"cursor_x"`
		CursorY       int      `json:"cursor_y"`
		CursorVisible bool     `json:"cursor_visible"`
	}{a.field.GetText(), a.changes, a.done, a.width, x, y, visible}, nil
}
