package main

import (
	"fmt"
	"github.com/gdamore/tcell/v3"
)

type adapter struct{ buffer *tcell.CellBuffer }

func (a *adapter) close() {}

// step exposes CellBuffer operations, including native grapheme and dirty state.
func (a *adapter) step(e event) (any, error) {
	rest := ""
	used := 0
	if e.Op == "new" || e.Op == "resize" {
		if e.Width < 1 || e.Width > 80 || e.Height < 1 || e.Height > 25 {
			return nil, fmt.Errorf("invalid dimensions")
		}
	}
	if e.Op == "new" {
		a.buffer = &tcell.CellBuffer{}
		a.buffer.Resize(e.Width, e.Height)
	} else if a.buffer == nil {
		return nil, fmt.Errorf("first event must be new")
	} else {
		switch e.Op {
		case "resize":
			a.buffer.Resize(e.Width, e.Height)
		case "put":
			if len(e.Text) > 4096 {
				return nil, fmt.Errorf("text too large")
			}
			rest, used = a.buffer.Put(e.X, e.Y, e.Text, tcell.StyleDefault)
		case "clean":
			a.buffer.SetDirty(e.X, e.Y, false)
		case "clear":
			a.buffer.Fill(' ', tcell.StyleDefault)
		default:
			return nil, fmt.Errorf("unsupported event")
		}
	}
	w, h := a.buffer.Size()
	cells := make([]any, 0, w*h)
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			text, _, width := a.buffer.Get(x, y)
			cells = append(cells, map[string]any{"text": text, "width": width, "dirty": a.buffer.Dirty(x, y)})
		}
	}
	return map[string]any{"width": w, "height": h, "cells": cells, "rest": rest, "used": used}, nil
}
