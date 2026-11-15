// Browser smoke test for an exported report. Uses an isolated headless browser.
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const root=path.resolve(process.argv[2]);
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROME_BINARY||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});try{
const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});await page.goto('file://'+path.join(root,'report.html'));await page.waitForFunction(()=>reportReady&&previewState);await page.evaluate(()=>document.fonts.ready);const data=JSON.parse(fs.readFileSync(path.join(root,'config/faceSettings-readable.json')));assert.equal(await page.locator('#expression option').count(),data.length);
for(let i=0;i<data.length;i++){await page.selectOption('#expression',String(i));await page.waitForFunction(p=>reportReady&&previewState.picture===p,data[i].picture);assert((await page.locator('#commands').textContent()).includes(data[i].picture))}
await page.selectOption('#expression','0');await page.waitForFunction(p=>reportReady&&previewState.picture===p,data[0].picture);await page.screenshot({path:path.join(root,'qa/report-desktop.png')});await page.selectOption('#slot','2');assert((await page.locator('#commands').textContent()).startsWith('\\F2['));assert(await page.locator('#mirror').isChecked());
await page.click('#speak');await page.click('#blink-once');const samples=await page.evaluate(()=>new Promise(resolve=>{const values=[];const timer=setInterval(()=>values.push({...previewState}),30);setTimeout(()=>{clearInterval(timer);resolve(values)},1150)}));assert.deepEqual([...new Set(samples.map(x=>x.mouth))].sort(),[0,1,2,3]);assert.deepEqual([...new Set(samples.map(x=>x.eye))].sort(),[0,1,2,3]);await page.click('#speak-off');await page.waitForFunction(()=>previewState.mouth===0&&!previewState.speaking);
await page.fill('#message','測試文字');await page.click('#message-play');await page.waitForFunction(()=>previewState.speaking===false&&previewState.mouth===0);
await page.click('#pause');await page.selectOption('#eye','2');await page.selectOption('#mouth','3');assert.equal(await page.evaluate(()=>previewState.eye),2);assert.equal(await page.evaluate(()=>previewState.mouth),3);await page.click('#step');
let bodyChecked=false;if(await page.locator('#body').isEnabled()){
 await page.check('#body');await page.waitForFunction(()=>previewState.body>=0);bodyChecked=true;
 assert(!(await page.locator('#body-loop').isChecked()));
 const bodyFrames=await page.evaluate(()=>{const seen=[];for(let i=0;i<80;i++){previewAPI.update();previewAPI.draw();seen.push(previewState.body)}return seen});
 assert.deepEqual([...new Set(bodyFrames)],[0,1,2,3]);assert.equal(bodyFrames.at(-1),3);
 assert((await page.locator('#commands').textContent()).includes('\\ACT'));
 await page.check('#body-loop');assert((await page.locator('#commands').textContent()).endsWith('\\loop'));
 const looping=await page.evaluate(()=>{const seen=[];for(let i=0;i<80;i++){previewAPI.update();previewAPI.draw();seen.push(previewState.body)}return seen});
 assert(looping.slice(61).some(x=>x===0||x===1));
 await page.screenshot({path:path.join(root,'qa/report-body.png')});await page.uncheck('#body')
}
await page.check('#roi');await page.screenshot({path:path.join(root,'qa/report-mirror-roi.png')});await page.setViewportSize({width:390,height:844});await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(root,'qa/report-mobile.png')});assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)),'Mobile overflow');assert.deepEqual(errors,[]);
const result={passed:true,offline_report:true,expressions:data.length,checks:['all exported expression image loads','short slot commands','mirror','four eye/mouth frames','OFF','message SPEAK stops','manual combinations','pause/step','390px layout'],body_preview_tested:bodyChecked,browser_errors:errors,engine_verification:'not_run'};fs.writeFileSync(path.join(root,'qa/browser-verification.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}finally{await browser.close()}})().catch(error=>{console.error(error);process.exit(1)});
