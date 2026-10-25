// This executable adapts native widget APIs to interaction-check JSONL.
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"unicode/utf8"

	"github.com/gdamore/tcell/v2"
)

type event struct {
	Op         string `json:"op"`
	Text       string `json:"text,omitempty"`
	Key        string `json:"key,omitempty"`
	Width      int    `json:"width,omitempty"`
	Position   int    `json:"position,omitempty"`
	DigitsOnly bool   `json:"digits_only,omitempty"`
}
type request struct {
	Protocol int    `json:"protocol"`
	ID       uint64 `json:"id"`
	Event    event  `json:"event"`
}

// keyMessage permits deterministic editing keys without clipboard access.
func keyMessage(name string) (*tcell.EventKey, error) {
	keys := map[string]tcell.Key{
		"left": tcell.KeyLeft, "right": tcell.KeyRight, "home": tcell.KeyHome, "end": tcell.KeyEnd,
		"backspace": tcell.KeyBackspace2, "delete": tcell.KeyDelete, "tab": tcell.KeyTab,
		"shift+tab": tcell.KeyBacktab, "enter": tcell.KeyEnter, "escape": tcell.KeyEscape,
		"ctrl+z": tcell.KeyCtrlZ, "ctrl+y": tcell.KeyCtrlY,
	}
	if key, ok := keys[name]; ok {
		return tcell.NewEventKey(key, 0, tcell.ModNone), nil
	}
	return nil, fmt.Errorf("unsupported key %q", name)
}

// run keeps protocol output separate from diagnostics and bounds each input line.
func run(in io.Reader, out io.Writer) error {
	scanner := bufio.NewScanner(in)
	scanner.Buffer(make([]byte, 4096), 64*1024)
	encoder := json.NewEncoder(out)
	var model adapter
	defer model.close()
	for scanner.Scan() {
		if !utf8.Valid(scanner.Bytes()) {
			return fmt.Errorf("request is not UTF-8")
		}
		var req request
		decoder := json.NewDecoder(bytes.NewReader(scanner.Bytes()))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&req); err != nil {
			return err
		}
		var extra any
		if err := decoder.Decode(&extra); err != io.EOF {
			return fmt.Errorf("expected one JSON object per line")
		}
		if req.Protocol != 1 {
			return fmt.Errorf("unsupported protocol %d", req.Protocol)
		}
		state, err := model.step(req.Event)
		if err != nil {
			return fmt.Errorf("event %d: %w", req.ID, err)
		}
		if err := encoder.Encode(struct {
			Protocol int    `json:"protocol"`
			ID       uint64 `json:"id"`
			State    any    `json:"state"`
		}{1, req.ID, state}); err != nil {
			return err
		}
	}
	return scanner.Err()
}

func main() {
	if err := run(os.Stdin, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
