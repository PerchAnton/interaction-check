package main

import (
	"errors"
	"fmt"
	"github.com/awesome-gocui/gocui"
	"strings"
)

type adapter struct {
	gui    *gocui.Gui
	screen gocui.TestingScreen
	stop   func()
}

// close stops the native simulated event loop after the last response.
func (a *adapter) close() {
	if a.stop != nil {
		a.stop()
		a.gui.Close()
		a.stop = nil
	}
}

// step uses gocui's built-in TestingScreen synchronization rather than sleeps.
func (a *adapter) step(e event) (any, error) {
	if e.Op == "new" {
		if a.gui != nil {
			return nil, fmt.Errorf("new is only allowed once per process")
		}
		if e.Width < 4 || e.Width > 60 {
			return nil, fmt.Errorf("invalid width")
		}
		var err error
		a.gui, err = gocui.NewGui(gocui.OutputSimulator, true)
		if err != nil {
			return nil, err
		}
		a.gui.SetManagerFunc(func(g *gocui.Gui) error {
			v, err := g.SetView("input", 0, 0, e.Width+1, 4, 0)
			if err != nil && !errors.Is(err, gocui.ErrUnknownView) {
				return err
			}
			if errors.Is(err, gocui.ErrUnknownView) {
				v.Editable = true
				v.Wrap = true
				_, err = g.SetCurrentView("input")
				return err
			}
			return nil
		})
		a.screen = a.gui.GetTestingScreen()
		a.stop = a.screen.StartGui()
	} else if a.gui == nil {
		return nil, fmt.Errorf("first event must be new")
	} else {
		switch e.Op {
		case "text":
			if len(e.Text) > 4096 {
				return nil, fmt.Errorf("text too large")
			}
			a.screen.SendStringAsKeys(e.Text)
			a.screen.WaitSync()
		case "key":
			keys := map[string]gocui.Key{"left": gocui.KeyArrowLeft, "right": gocui.KeyArrowRight, "home": gocui.KeyHome, "end": gocui.KeyEnd, "backspace": gocui.KeyBackspace2, "delete": gocui.KeyDelete, "enter": gocui.KeyEnter}
			key, ok := keys[e.Key]
			if !ok {
				return nil, fmt.Errorf("unsupported key")
			}
			a.screen.SendKeySync(key)
		default:
			return nil, fmt.Errorf("unsupported event")
		}
	}
	v, err := a.gui.View("input")
	if err != nil {
		return nil, err
	}
	x, y := v.Cursor()
	ox, oy := v.Origin()
	return map[string]any{"value": strings.TrimSuffix(v.Buffer(), "\n"), "cursor": []int{x, y}, "origin": []int{ox, oy}}, nil
}
