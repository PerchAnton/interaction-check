// This executable observes a native Go API through bounded JSONL requests.
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"unicode/utf8"
)

type event struct {
	Op         string `json:"op"`
	Text       string `json:"text,omitempty"`
	Key        string `json:"key,omitempty"`
	Width      int    `json:"width,omitempty"`
	Height     int    `json:"height,omitempty"`
	X          int    `json:"x,omitempty"`
	Y          int    `json:"y,omitempty"`
	Dirty      bool   `json:"dirty,omitempty"`
	DigitsOnly bool   `json:"digits_only,omitempty"`
	CharLimit  int    `json:"char_limit,omitempty"`
}
type request struct {
	Protocol int    `json:"protocol"`
	ID       uint64 `json:"id"`
	Event    event  `json:"event"`
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
