package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	jsonpatch "github.com/evanphx/json-patch/v5"
	"github.com/wI2L/jsondiff"
	"os"
)

type event struct {
	Op     string          `json:"op"`
	Data   json.RawMessage `json:"data"`
	Patch  json.RawMessage `json:"patch"`
	Target json.RawMessage `json:"target"`
}
type request struct {
	Protocol int   `json:"protocol"`
	ID       int   `json:"id"`
	Event    event `json:"event"`
}

func apply(document, patch []byte) ([]byte, error) {
	decoded, err := jsonpatch.DecodePatch(patch)
	if err != nil {
		return nil, err
	}
	options := jsonpatch.NewApplyOptions()
	options.SupportNegativeIndices = false
	return decoded.ApplyWithOptions(document, options)
}
func main() {
	document := json.RawMessage(`null`)
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 4096), 1<<20)
	for scanner.Scan() {
		var req request
		if err := json.Unmarshal(scanner.Bytes(), &req); err != nil {
			panic(err)
		}
		if req.Protocol != 1 {
			panic("invalid protocol")
		}
		var failure any
		switch req.Event.Op {
		case "new":
			document = req.Event.Data
		case "apply":
			result, err := apply(document, req.Event.Patch)
			if err != nil {
				failure = "rejected"
			} else {
				document = result
			}
		case "diff":
			patch, err := jsondiff.CompareJSON(document, req.Event.Target)
			if err != nil {
				panic(err)
			}
			encoded, err := json.Marshal(patch)
			if err != nil {
				panic(err)
			}
			result, err := apply(document, encoded)
			if err != nil {
				panic(err)
			}
			document = result
		default:
			panic("unknown event")
		}
		response := map[string]any{"protocol": 1, "id": req.ID, "state": map[string]any{"document": document, "error": failure}}
		encoded, err := json.Marshal(response)
		if err != nil {
			panic(err)
		}
		fmt.Println(string(encoded))
	}
	if err := scanner.Err(); err != nil {
		panic(err)
	}
}
