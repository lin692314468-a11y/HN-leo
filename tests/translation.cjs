const fs=require('fs'),vm=require('vm'),assert=require('assert');
vm.runInThisContext(fs.readFileSync('dist/translation.js','utf8'));
global.location={origin:'http://127.0.0.1:8765'};global.langs={de:'德语'};
const config={priority:'deepl',deeplKey:'test:fx',deeplPlan:'auto',endpoint:'https://example.invalid/chat',key:'test',model:'test'};
(async()=>{
assert.deepEqual(translationProviders({...config,deeplKey:''}).map(p=>p.id),['chat']);
assert.deepEqual(translationProviders({...config,key:''}).map(p=>p.id),['deepl']);
assert.equal(translationProviders({...config,key:'',deeplKey:''}).length,0);
let calls=[],state={active:null,disabled:new Set()};
const mock=async(url,opts)=>{calls.push(url);return url==='/api/deepl'?{ok:false,status:502,json:async()=>({error:'配额已用尽',upstreamStatus:456})}:{ok:true,json:async()=>({choices:[{message:{content:'Hallo'}}]})}};
let result=await translateWithFallback('Hello','de',config,state,()=>{},mock);
assert.equal(result.text,'Hallo');assert.equal(state.active,'chat');assert(state.disabled.has('deepl'));assert.equal(calls.length,2);
calls=[];await translateWithFallback('Hello','de',config,state,()=>{},mock);assert.equal(calls.length,1);assert.equal(calls[0],config.endpoint);
state={active:null,disabled:new Set()};calls=[];const reverse=async url=>{calls.push(url);return url==='/api/deepl'?{ok:true,json:async()=>({text:'Hallo'})}:{ok:false,status:401,json:async()=>({})}};
await translateWithFallback('Hello','de',{...config,priority:'chat'},state,()=>{},reverse);assert.deepEqual(calls,[config.endpoint,'/api/deepl']);
let invalid=async()=>({ok:true,json:async()=>({})});await assert.rejects(()=>translateWithFallback('x','de',config,{active:null,disabled:new Set()},()=>{},invalid),/有效译文/);
console.log('PASS: single-provider, no-config, both fallback directions, quota circuit break, sticky success, invalid responses');
})().catch(e=>{console.error(e);process.exit(1)});
