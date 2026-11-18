import { apply } from 'mutative';

// Deliberately bounded RFC 6902 subset, for JSON object documents in this example.
// Mutative performs each mutation; this bridge translates paths and move/copy.
export function pointer(value) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.length > 4096) {
    throw new Error('non-root JSON Pointer required');
  }
  return value.slice(1).split('/').map(part => {
    if (/~(?:[^01]|$)/.test(part)) throw new Error('invalid pointer escape');
    const decoded = part.replaceAll('~1', '/').replaceAll('~0', '~');
    if (['__proto__', 'prototype', 'constructor'].includes(decoded)) throw new Error('reserved path');
    return decoded;
  });
}

export function validatePatch(patch) {
  if (!Array.isArray(patch) || patch.length > 64) throw new Error('at most 64 operations');
  for (const item of patch) {
    const op = item?.op;
    const required = ['add', 'replace'].includes(op) ? ['op', 'path', 'value']
      : ['move', 'copy'].includes(op) ? ['op', 'path', 'from'] : op === 'remove' ? ['op', 'path'] : [];
    if (!required.length || !item || typeof item !== 'object' || Array.isArray(item)
      || Object.keys(item).length !== required.length || required.some(key => !Object.hasOwn(item, key))) {
      throw new Error('unsupported patch operation or fields');
    }
    pointer(item.path);
    if ('from' in item) pointer(item.from);
  }
}

function locate(document, tokens, adding = false) {
  let parent = document;
  const path = [];
  for (let index = 0; index < tokens.length; index++) {
    const last = index === tokens.length - 1;
    let key = tokens[index];
    if (Array.isArray(parent)) {
      if (key === '-' && adding && last) key = parent.length;
      else {
        if (!/^(0|[1-9][0-9]*)$/.test(key)) throw new Error('invalid array index');
        key = Number(key);
        if (!Number.isSafeInteger(key) || key > parent.length || (key === parent.length && !(last && adding))) {
          throw new Error('array index out of bounds');
        }
      }
    } else if (!parent || typeof parent !== 'object') throw new Error('path parent is not a container');
    if (!(last && adding) && !Object.hasOwn(parent, key)) throw new Error('missing path');
    path.push(key);
    if (last) return { path, value: parent[key] };
    parent = parent[key];
  }
  throw new Error('root operations are outside this example');
}

export function applyBridge(document, patch) {
  validatePatch(patch);
  let result = document;
  for (const item of patch) {
    const target = pointer(item.path);
    if (item.op === 'move' || item.op === 'copy') {
      const origin = pointer(item.from);
      const source = locate(result, origin);
      if (item.op === 'move') {
        if (target.length > origin.length && origin.every((v, i) => target[i] === v)) {
          throw new Error('cannot move into a descendant');
        }
        if (target.length === origin.length && origin.every((v, i) => target[i] === v)) continue;
        result = apply(result, [{ op: 'remove', path: source.path }]);
      }
      result = apply(result, [{ op: 'add', path: locate(result, target, true).path,
        value: structuredClone(source.value) }]);
    } else {
      const operation = { op: item.op, path: locate(result, target, item.op === 'add').path };
      if ('value' in item) operation.value = structuredClone(item.value);
      result = apply(result, [operation]);
    }
  }
  return result;
}
