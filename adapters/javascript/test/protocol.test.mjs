import { test } from "node:test";
import assert from "node:assert/strict";
import { Readable, Writable } from "node:stream";
import { decode, serve, fields, text, index } from "../protocol.mjs";

const envelope = (event, id = 0) => ({ protocol: 1, id, event });
const bytes = (value) => Buffer.from(JSON.stringify(value));

test("rejects expectations and malformed envelope types before executing native code", () => {
  for (const value of [
    { ...envelope({}), expect: { text: "fake" } },
    envelope({}, true),
    envelope({}, -1),
    envelope({}, 1.5),
    envelope([]),
    envelope(null),
    { ...envelope({}), protocol: true },
    { ...envelope({}), protocol: 2 },
  ])
    assert.throws(() => decode(bytes(value)));
});

test("rejects malformed UTF-8 and oversized records", () => {
  assert.throws(() => decode(Buffer.from([0xff])));
  assert.throws(() => decode(Buffer.alloc(65537, 32)));
});

test("fragmented multibyte input, CRLF and final record retain order and IDs", async () => {
  const input = Buffer.from(
    JSON.stringify(envelope({ text: "🙂\u2028界" }, 7)) +
      "\r\n" +
      JSON.stringify(envelope({ text: "two" }, 8)),
  );
  let output = "";
  await serve(
    async (e) => ({ actual: e.text }),
    Readable.from([...input].map((b) => Buffer.from([b]))),
    new Writable({
      write(chunk, encoding, done) {
        output += chunk;
        done();
      },
    }),
  );
  assert.deepEqual(
    output
      .trim()
      .split("\n")
      .map((line) => JSON.parse(line)),
    [
      { protocol: 1, id: 7, state: { actual: "🙂\u2028界" } },
      { protocol: 1, id: 8, state: { actual: "two" } },
    ],
  );
});

test("rejects an unterminated huge line before calling the adapter", async () => {
  let called = false;
  await assert.rejects(
    serve(
      () => {
        called = true;
      },
      Readable.from([Buffer.alloc(65537)]),
    ),
  );
  assert.equal(called, false);
});

test("event fields, Unicode and integer bounds fail explicitly", () => {
  assert.throws(() => fields({ op: "new", expect: {} }, ["op"]));
  for (const value of [true, -1, 1.5, 5]) assert.throws(() => index(value, 4));
  for (const value of ["\ud800", "x".repeat(4097), null])
    assert.throws(() => text(value));
});

test("oversized native state fails instead of flooding stdout", async () => {
  await assert.rejects(
    serve(
      () => ({ text: "x".repeat(65536) }),
      Readable.from([bytes(envelope({}))]),
    ),
    /state exceeds/,
  );
});
