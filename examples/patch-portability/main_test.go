package main

import (
	"encoding/json"
	jsonpatch "github.com/evanphx/json-patch/v5"
	"github.com/wI2L/jsondiff"
	"testing"
)

func TestDiffRoundTrip(t *testing.T) {
	before := []byte(`{"items":["a","a","b"],"a/b":"old"}`)
	target := []byte(`{"items":["a","b","b"],"a/b":"new\\"}`)
	for _, options := range [][]jsondiff.Option{nil, {jsondiff.Rationalize()}, {jsondiff.Factorize()}} {
		patch, err := jsondiff.CompareJSON(before, target, options...)
		if err != nil {
			t.Fatal(err)
		}
		encoded, err := json.Marshal(patch)
		if err != nil {
			t.Fatal(err)
		}
		actual, err := apply(before, encoded)
		if err != nil {
			t.Fatal(err)
		}
		if !jsonpatch.Equal(actual, target) {
			t.Fatalf("target mismatch: %s", actual)
		}
	}
}
func TestFailedPatchDoesNotChangePublishedInput(t *testing.T) {
	before := []byte(`{"n":1}`)
	_, err := apply(before, []byte(`[{"op":"replace","path":"/n","value":2},{"op":"test","path":"/n","value":9}]`))
	if err == nil {
		t.Fatal("expected rejection")
	}
	if string(before) != `{"n":1}` {
		t.Fatal("input mutated")
	}
}
