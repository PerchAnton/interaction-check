import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
const [library, modulePath] = process.argv.slice(2);
const load = async suffix => import(modulePath ? pathToFileURL(modulePath + suffix).href : library + suffix);
const results = [];
if (library === 'rfc6902') {
 const { applyPatch } = await load(modulePath ? '/index.js' : '');
 for(const op of ['replace','copy','move'])for(const token of ['-1','00','1.5']) {
  const doc={list:[1,2],source:'S'};const before=structuredClone(doc);
  const patch={op,path:'/list/'+token,...(op==='replace'?{value:9}:{from:'/source'})};
  const errors=applyPatch(doc,[patch]);
  let unchanged=true;try{assert.deepEqual(doc,before)}catch{unchanged=false}
  results.push({op,token,rejected:errors.some(Boolean),unchanged,ownKeys:Object.keys(doc.list),document:doc});
 }
} else if(library==='fast-json-patch') {
 const m=await load(modulePath?'/index.js':'');const api=m.default??m;
 for(const value of [0,false,'',null]) {
  let error=null;try{api.applyPatch(value,[{op:'add',path:'/child',value:1}],true)}catch(e){error={name:e.name,constructor:e.constructor.name}}
  const replacement=api.applyPatch(value,[{op:'replace',path:'',value:{ok:true}}],true).newDocument;
  results.push({value,error,replacement});
 }
} else if(library==='jsondiffpatch') {
 const plain=await load(modulePath?'/lib/index.js':'');
 const text=await load(modulePath?'/lib/with-text-diffs.js':'/with-text-diffs');
 const formatter=await load(modulePath?'/lib/formatters/jsonpatch.js':'/formatters/jsonpatch');
 const a={text:'The quick brown fox jumps over the lazy dog. '.repeat(3)};
 const b={text:a.text.replace('dog','cat')};
 const p=plain.create();const before=formatter.format(p.diff(a,b));text.create().diff(a,b);
 for(const [name,instance] of [['existing',p],['fresh',plain.create()]]) {
  const delta=instance.diff(a,b);let patch=null,error=null;try{patch=formatter.format(delta)}catch(e){error=e.message}
  results.push({name,before,delta,patch,error,unchanged:JSON.stringify(patch)===JSON.stringify(before)});
 }
} else throw new Error('Unknown probe');
console.log(JSON.stringify({library,module:modulePath??'published',results},null,2));
