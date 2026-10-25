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

	tea "charm.land/bubbletea/v2"
)

type event struct {
	Op       string `json:"op"`
	Text     string `json:"text,omitempty"`
	Key      string `json:"key,omitempty"`
	Width    int    `json:"width,omitempty"`
	Position int    `json:"position,omitempty"`
}
type request struct {
	Protocol int    `json:"protocol"`
	ID       uint64 `json:"id"`
	Event    event  `json:"event"`
}

// keyMessage permits only deterministic editing keys, never clipboard commands.
func keyMessage(name string) (tea.KeyPressMsg, error) {
	keys := map[string]tea.KeyPressMsg{
		"left": {Code: tea.KeyLeft}, "right": {Code: tea.KeyRight},
		"home": {Code: tea.KeyHome}, "end": {Code: tea.KeyEnd},
		"backspace": {Code: tea.KeyBackspace}, "delete": {Code: tea.KeyDelete},
		"tab": {Code: tea.KeyTab}, "shift+tab": {Code: tea.KeyTab, Mod: tea.ModShift},
		"enter": {Code: tea.KeyEnter}, "escape": {Code: tea.KeyEscape},
		"ctrl+c": {Code: 'c', Mod: tea.ModCtrl}, "ctrl+a": {Code: 'a', Mod: tea.ModCtrl},
		"ctrl+e": {Code: 'e', Mod: tea.ModCtrl},
	}
	if k, ok := keys[name]; ok {
		return k, nil
	}
	return tea.KeyPressMsg{}, fmt.Errorf("unsupported key %q", name)
}

// run keeps protocol output separate from diagnostics and bounds each input line.
func run(in io.Reader, out io.Writer) error {
	scanner := bufio.NewScanner(in)
	scanner.Buffer(make([]byte, 4096), 64*1024)
	encoder := json.NewEncoder(out)
	var model adapter
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
