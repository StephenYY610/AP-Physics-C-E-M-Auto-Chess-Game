const LEVEL_TO_FIELD_LIMIT={1:1,2:2,3:2,4:3,5:3,6:4,7:4,8:5};
const XP_TO_NEXT={1:2,2:4,3:6,4:10,5:20,6:32,7:50,8:0};
const ROLL_ODDS={1:{1:1},2:{1:.75,2:.25},3:{1:.55,2:.35,3:.1},4:{1:.35,2:.4,3:.2,4:.05},5:{1:.2,2:.35,3:.3,4:.13,5:.02},6:{1:.1,2:.25,3:.35,4:.25,5:.05},7:{1:.05,2:.15,3:.3,4:.35,5:.15},8:{1:.02,2:.08,3:.22,4:.38,5:.3}};
const BASE_DAMAGE={1:{correct:3,wrong:2,timeout:3},2:{correct:5,wrong:3,timeout:5},3:{correct:8,wrong:5,timeout:8},4:{correct:12,wrong:8,timeout:12},5:{correct:18,wrong:12,timeout:18}};
const SYNERGIES={electrostatics:[2,3,5],gauss:[1,3,4],circuits:[2,3,4],magnetism:[2,4,5],induction:[1,2,4,5],potential:[2,3,5],differential:[1,3,5],combined:[1,2,3]};
const SYNERGY_DAMAGE={electrostatics:{2:2,3:4,5:7},gauss:{1:2,3:5,4:8},circuits:{2:2,3:4,4:6},magnetism:{2:2,4:5,5:7},induction:{1:1,2:3},potential:{2:2,3:4},differential:{1:2,3:5},combined:{1:3,2:6,3:10}};
const POOL=[
{name:"Field Direction",cost:1,tags:["electrostatics"],q:"Does electric field point from + to -?",a:"yes"},
{name:"Ohm Quick",cost:2,tags:["circuits"],q:"Formula for voltage in resistor?",a:"V=IR"},
{name:"Lorentz Force",cost:2,tags:["magnetism"],q:"Magnetic force formula?",a:"F=qvB"},
{name:"Gauss Shell",cost:3,tags:["gauss"],q:"Outside a spherical shell E behaves as?",a:"kQ/r^2"},
{name:"RC Initial",cost:3,tags:["circuits","differential"],q:"At t=0 charging capacitor is like?",a:"short"},
{name:"Potential+Field",cost:4,tags:["potential","combined"],q:"Relation between E and V in 1D?",a:"E=-dV/dx"},
{name:"Faraday Final",cost:5,tags:["induction","magnetism","combined"],q:"Induced EMF formula?",a:"emf=-dphi/dt"}
];

const state={round:1,phase:'shop',activePlayer:0,players:[mkPlayer('Player 1'),mkPlayer('Player 2')],shop:[],battleLog:[]};
function mkPlayer(name){return {name,hp:100,gold:10,level:1,xp:0,bench:[],fielded:[],streak:0};}

function weightedCost(level){const odds=ROLL_ODDS[level]; let r=Math.random(),a=0; for(const k of [1,2,3,4,5]){a+=(odds[k]||0); if(r<=a) return k;} return 1;}
function rollShop(player){state.shop=Array.from({length:5},()=>{const cost=weightedCost(player.level); const c=POOL.filter(p=>p.cost===cost); return JSON.parse(JSON.stringify(c[Math.floor(Math.random()*c.length)]));});}
function addXP(p,amt){if(p.level>=8)return; p.xp+=amt; while(p.level<8&&p.xp>=XP_TO_NEXT[p.level]){p.xp-=XP_TO_NEXT[p.level]; p.level++;}}
function tier(tag,count){let t=0; for(const n of SYNERGIES[tag]) if(count>=n) t=n; return t;}
function render(){
  document.getElementById('status').innerHTML=`<b>Round ${state.round}</b> | Phase: ${state.phase} | Active: ${state.players[state.activePlayer].name}`;
  state.players.forEach((p,i)=>{document.getElementById(`player-${i}`).innerHTML=`<h3>${p.name}</h3><p>HP ${p.hp} | Gold ${p.gold} | Lv ${p.level} | XP ${p.xp}/${p.level<8?XP_TO_NEXT[p.level]:'MAX'}</p><button onclick="setField(${i})">Auto Set Field</button><button onclick="buyXP(${i})">Buy 4 XP (4g)</button><div><b>Bench</b>${p.bench.map((u,idx)=>`<div class='unit'>${u.name} C${u.cost} ⭐${u.star||1} <button onclick='sellUnit(${i},${idx})'>Sell</button></div>`).join('')}</div><div><b>Field</b>${p.fielded.map(u=>`<div class='unit'>${u.name} C${u.cost} ⭐${u.star||1}</div>`).join('')}</div>`;});
  document.getElementById('shop-controls').innerHTML=`<button onclick='reroll()'>Reroll (2g)</button>`;
  document.getElementById('shop').innerHTML=state.shop.map((u,idx)=>`<div class='unit shop-item'><b>${u.name}</b><br/>Cost ${u.cost}<br/>Tags: ${u.tags.join(', ')}<br/><button onclick='buyUnit(${idx})'>Buy</button></div>`).join('');
  document.getElementById('battle').innerHTML=state.battleLog.slice(-8).map(l=>`<div>${l}</div>`).join('');
}
function mergeStars(p){const map={}; p.bench.forEach((u,i)=>{u.star=u.star||1; const k=u.name+'|'+u.star; (map[k]=map[k]||[]).push(i);}); for(const k in map){const ids=map[k]; if(ids.length>=3){const keep=ids[0],r=[ids[1],ids[2]].sort((a,b)=>b-a); p.bench[keep].star++; r.forEach(i=>p.bench.splice(i,1)); return mergeStars(p);}}}
function buyUnit(i){const p=state.players[state.activePlayer],u=state.shop[i]; if(!u||u.cost>p.gold||p.bench.length>=9) return; p.gold-=u.cost; p.bench.push({...u,star:1}); state.shop.splice(i,1); mergeStars(p); render();}
function sellUnit(pi,idx){const p=state.players[pi],u=p.bench[idx]; if(!u)return; p.gold+=Math.max(1,Math.floor(u.cost/2)); p.bench.splice(idx,1); render();}
function reroll(){const p=state.players[state.activePlayer]; if(p.gold<2)return; p.gold-=2; rollShop(p); render();}
function buyXP(i){const p=state.players[i]; if(p.gold<4)return; p.gold-=4; addXP(p,4); render();}
function setField(i){const p=state.players[i]; p.fielded=[...p.bench].sort((a,b)=>(b.star-a.star)||(b.cost-a.cost)).slice(0,LEVEL_TO_FIELD_LIMIT[p.level]); render();}

function endShopTurn(){if(state.activePlayer===0){state.activePlayer=1; rollShop(state.players[1]);} else {state.activePlayer=0; state.phase='battle'; battle();} render();}
document.getElementById('end-shop').onclick=endShopTurn;

function battle(){state.battleLog.push(`<b>Battle Round ${state.round}</b>`); for(let atk=0; atk<2; atk++){const a=state.players[atk],d=state.players[1-atk]; const counts={electrostatics:0,gauss:0,circuits:0,magnetism:0,induction:0,potential:0,differential:0,combined:0}; a.fielded.forEach(u=>u.tags.forEach(t=>counts[t]++)); let circuitsCorrect=0;
    a.fielded.forEach(u=>{const ans=prompt(`${a.name} asks ${d.name}: ${u.name}\n${u.q}\n(Type answer; leave blank for timeout)`,''); let result='timeout'; if(ans!==null&&ans.trim()!==''){result=ans.trim().toLowerCase()===u.a.toLowerCase()?'correct':'wrong';}
      if(result==='correct'){let dmg=Math.floor(BASE_DAMAGE[u.cost].correct*(u.star===2?1.5:u.star===3?2:1)); u.tags.forEach(t=>{const tt=tier(t,counts[t]); dmg+= (SYNERGY_DAMAGE[t]&&SYNERGY_DAMAGE[t][tt])||0; if(t==='magnetism'&&tt===5&&Math.random()<0.3) dmg*=2; if(t==='induction'&&tt===4) dmg+=3; if(t==='induction'&&tt===5) dmg+=Math.floor(dmg*0.4);}); if(u.tags.includes('differential')&&tier('differential',counts.differential)===5) d.hp-=6; d.hp-=dmg; if(u.tags.includes('circuits')) circuitsCorrect++; state.battleLog.push(`<span class='good'>${a.name} correct on ${u.name}: -${dmg} HP to ${d.name}</span>`);} else {const loss=BASE_DAMAGE[u.cost][result]; a.hp-=loss; state.battleLog.push(`<span class='bad'>${a.name} ${result} on ${u.name}: -${loss} self HP</span>`);} }); if(tier('circuits',counts.circuits)===4&&circuitsCorrect>=2){d.hp-=3; state.battleLog.push(`<span class='good'>${a.name} circuits combo: extra 3 damage.</span>`);} }
  settlement();
}
function settlement(){state.players.forEach(p=>{p.gold+=5; addXP(p,2); if(p.hp<0)p.hp=0;}); const [p1,p2]=state.players; if(p1.hp<=0||p2.hp<=0){state.phase='gameover'; state.battleLog.push(`<b>Winner: ${p1.hp>p2.hp?p1.name:p2.name}</b>`); return;} state.phase='shop'; state.round++; state.activePlayer=0; rollShop(state.players[0]);}

rollShop(state.players[0]); render();
