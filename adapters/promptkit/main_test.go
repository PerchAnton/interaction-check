package main

import (
	"bytes"
	"strings"
	"testing"
)

// TestRejectInvalidEnvelope ensures malformed requests never produce a state.
func TestRejectInvalidEnvelope(t *testing.T) {
	for _, line := range []string{
		`{"protocol":2,"id":0,"event":{"op":"new","width":20,"height":1}}`,
		`{"protocol":1,"id":0,"event":{"op":"text","text":"x"}}`,
		`{"protocol":1,"id":0,"event":{"op":"new"},"expect":{}}`,
		`{"protocol":1,"id":0,"event":{"op":"new"}} {}`,
		strings.Repeat("x", 65537), string([]byte{255}),
	} {
		var out bytes.Buffer
		if err := run(strings.NewReader(line), &out); err == nil {
			t.Fatal("accepted invalid request")
		}
		if out.Len() != 0 {
			t.Fatal("invalid request produced state")
		}
	}
}

// TestPreserveRequestID checks the real native initialization round trip.
func TestPreserveRequestID(t *testing.T) {
	var out bytes.Buffer
	err := run(strings.NewReader(`{"protocol":1,"id":123,"event":{"op":"new","width":20,"height":1}}`), &out)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out.String(), `"id":123`) {
		t.Fatal("request ID lost")
	}
}
