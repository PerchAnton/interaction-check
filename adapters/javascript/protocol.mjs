import { once } from "node:events";

const limit = 65536;

export function fields(event, required, optional = []) {
  if (
    !event ||
    typeof event !== "object" ||
    Array.isArray(event) ||
    required.some((key) => !Object.hasOwn(event, key)) ||
    Object.keys(event).some(
      (key) => !required.includes(key) && !optional.includes(key),
    )
  ) {
    throw new Error("invalid event fields");
  }
}

export function text(value) {
  if (
    typeof value !== "string" ||
    value.length > 4096 ||
    !value.isWellFormed()
  ) {
    throw new Error("text must contain at most 4096 valid UTF-16 units");
  }
  return value;
}

export function index(value, maximum = 16384) {
  if (!Number.isSafeInteger(value) || value < 0 || value > maximum) {
    throw new Error(`index must be an integer between 0 and ${maximum}`);
  }
  return value;
}

export function choice(value, allowed) {
  if (!allowed.includes(value)) throw new Error("unsupported choice");
  return value;
}

export function decode(line) {
  if (line.length > limit) throw new Error("request exceeds 64 KiB");
  const request = JSON.parse(
    new TextDecoder("utf-8", { fatal: true }).decode(line),
  );
  fields(request, ["protocol", "id", "event"]);
  if (
    request.protocol !== 1 ||
    !Number.isSafeInteger(request.id) ||
    request.id < 0
  ) {
    throw new Error("invalid protocol or id");
  }
  if (
    !request.event ||
    typeof request.event !== "object" ||
    Array.isArray(request.event)
  ) {
    throw new Error("event must be an object");
  }
  return request;
}

export async function serve(
  step,
  input = process.stdin,
  output = process.stdout,
) {
  let pending = Buffer.alloc(0);
  let count = 0;
  async function reply(line) {
    if (++count > 1024) throw new Error("too many events");
    const request = decode(line);
    const state = await step(request.event);
    const response =
      JSON.stringify({ protocol: 1, id: request.id, state }) + "\n";
    if (Buffer.byteLength(response) > limit)
      throw new Error("state exceeds 64 KiB");
    if (!output.write(response)) await once(output, "drain");
  }
  for await (const chunk of input) {
    pending = Buffer.concat([pending, chunk]);
    let boundary;
    while ((boundary = pending.indexOf(10)) >= 0) {
      await reply(pending.subarray(0, boundary));
      pending = pending.subarray(boundary + 1);
    }
    if (pending.length > limit) throw new Error("request exceeds 64 KiB");
  }
  if (pending.length) await reply(pending);
}
