// Execute the exported real plugin with empty user faceSettings and minimal MZ stubs.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(process.argv[2]),expected=Number(process.argv[3]),manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'))),configs=JSON.parse(fs.readFileSync(path.join(root,'config/faceSettings-readable.json'))),source=fs.readFileSync(path.join(root,manifest.generated_plugin),'utf8');
function Sprite(){this.initialize()}Sprite.prototype.initialize=function(){this.children=[];this.scale={x:1,y:1};this.x=this.y=0;this.opacity=255;this.visible=true};Sprite.prototype.addChild=function(c){this.children.push(c)};Sprite.prototype.addChildAt=function(c,i){this.children.splice(i,0,c)};Sprite.prototype.setFrame=function(x,y,w,h){this.frame={x,y,w,h}};Sprite.prototype.setColorTone=Sprite.prototype.setBlendColor=Sprite.prototype.update=function(){};Object.defineProperties(Sprite.prototype,{width:{get(){return (this.bitmap?.width||0)*Math.abs(this.scale.x)}},height:{get(){return (this.bitmap?.height||0)*Math.abs(this.scale.y)}}});
function Empty(){};Empty.prototype.initialize=Empty.prototype.createDisplayObjects=Empty.prototype.update=function(){};function Window_Base(){};Window_Base.prototype.convertEscapeCharacters=t=>t;function Window_Message(){};Window_Message.prototype=Object.create(Window_Base.prototype);for(const k of['startMessage','processEscapeCharacter','onEndOfText','terminateMessage','updateClose'])Window_Message.prototype[k]=function(){};
const commands={},loaded=[],math=Object.create(Math);math.randomInt=()=>0;
const ctx={console,Math:math,document:{currentScript:{src:manifest.generated_plugin}},PluginManager:{parameters:()=>({faceSettings:'[]',profiles:'[]'}),registerCommand:(n,k,f)=>commands[k]=f},Sprite,Game_System:Empty,Scene_Map:Empty,Scene_Battle:Empty,Window_Base,Window_Message,$gameSystem:{},$gameVariables:{value:()=>0},$gameMessage:{allText:()=>''},ImageManager:{loadPicture:name=>{loaded.push(name);const b=fs.readFileSync(path.join(root,'runtime/img/pictures',name+'.png'));return {width:b.readUInt32BE(16),height:b.readUInt32BE(20),isReady:()=>true,addLoadListener:f=>f()}}}};vm.createContext(ctx);vm.runInContext(source.replace(/\}\)\(\);\s*$/,'globalThis.testAPI={faceSettings,pictureFor,StandingPictureDirect,Sprite_StandingPictureDirect,state};})();'),ctx);
assert.equal(configs.length,expected);if(configs[0]?.picture.startsWith('Phebe_'))assert.equal(ctx.testAPI.faceSettings.size,expected);
for(const c of configs){const face=ctx.testAPI.faceSettings.get(c.picture);assert(face);assert.equal(face.baseImage,c.baseImage);assert.equal(face.eyes.image,c.eyeImage);assert.equal(face.mouth.image,c.mouthImage);const s=new ctx.testAPI.Sprite_StandingPictureDirect();ctx.testAPI.StandingPictureDirect.refresh(s,ctx.testAPI.pictureFor(c.picture),1,[0,0,0,0]);assert(s.showing);assert.equal(s._face.x,c.faceX);assert.equal(s._face.y,c.faceY);commands.processChar({text:'\\F1['+c.picture+']\\FH[ON]\\SPEAK[1]'});assert(ctx.testAPI.state().pictures[0].speaking)}
const bodyFile=path.join(root,'config/bodyMotions-readable.json');const bodies=fs.existsSync(bodyFile)?JSON.parse(fs.readFileSync(bodyFile)):[];
for(const b of bodies){
 commands.processChar({text:'\\F1['+configs[0].picture+']\\FH[ON]\\ACT1['+b.id+']'});
 const slot=ctx.testAPI.state().pictures[0],s=new ctx.testAPI.Sprite_StandingPictureDirect();
 ctx.testAPI.StandingPictureDirect.refresh(s,slot.picture,1,[0,0,0,0]);s.opacity=255;s.opening=s.closing=false;
 const frames=[];for(let i=0;i<b.frameWait*4+1;i++){s.updateBody(slot);frames.push(Math.floor(s._body.frame.x/b.frameWidth)+1)}
 if(b.columns===4)assert.deepEqual([...new Set(frames)],[1,2,3,4]);
 assert.equal(slot.bodyMotion?.loop??false,false);
 commands.processChar({text:'\\ACT1['+b.id+']\\loop'});assert(slot.bodyMotion.loop);
 commands.processChar({text:'\\ACT1[OFF]'});s.updateBody(slot);assert(!s._body.visible);
}
assert(loaded.every(n=>!n.startsWith('old/')));console.log(JSON.stringify({passed:true,external_face_settings:0,expressions:configs.length,native_body_motions:bodies.length}));
