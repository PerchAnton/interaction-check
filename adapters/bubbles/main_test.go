package main

import (
	"bytes"
	"strings"
	"testing"
)

func TestRejectInvalidProtocol(t *testing.T) {
	cases := []string{
		`{"protocol":2,"id":0,"event":{"op":"new","width":40}}`,
		`{"protocol":1,"id":0,"event":{"op":"text","text":"x"}}`,
		`{"protocol":1,"id":0,"event":{"op":"new","width":-1}}`,
		`{"protocol":1,"id":0,"event":{"op":"new","width":40},"expect":{}}`,
		`{"protocol":1,"id":0,"event":{"op":"new","width":40}} {}`,
		strings.Repeat("x", 65537),
	}
	for _, line := range cases {
		var output bytes.Buffer
		if err := run(strings.NewReader(line), &output); err == nil {
			t.Fatalf("accepted invalid request %.80s", line)
		}
		if output.Len() != 0 {
			t.Fatalf("invalid request produced response: %s", output.String())
		}
	}
}

func TestPreserveRequestID(t *testing.T) {
	var output bytes.Buffer
	if err := run(strings.NewReader(`{"protocol":1,"id":123,"event":{"op":"new","width":40}}`), &output); err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(output.String(), `"id":123`) {
		t.Fatalf("request ID lost: %s", output.String())
	}
}
