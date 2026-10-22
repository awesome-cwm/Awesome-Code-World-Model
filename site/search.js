/* Taxonomy V2: one primary research area, any number of auxiliary filter tags. */
(function (root, factory) {
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.CWM_SEARCH=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function tagOptions(taxonomy){
    return taxonomy.tag_dimensions.flatMap(d=>Object.entries(d.values).map(([id,name])=>({id,name,dimension:d.id,dimensionName:d.name})));
  }
  function tagIds(classification){return Object.values(classification.tags).flat();}
  function readFilters(params,taxonomy){
    const areas=new Set(taxonomy.research_areas.map(a=>a.id));
    const directions=new Map(taxonomy.research_areas.flatMap(a=>a.directions.map(d=>[d.id,a.id])));
    const allowedTags=new Set(tagOptions(taxonomy).map(t=>t.id));
    let area=areas.has(params.get('area'))?params.get('area'):'all';
    let direction=params.get('direction')||'all';
    const parent=directions.get(direction);
    if(parent&&(area==='all'||area===parent))area=parent;
    else direction='all';
    const tags=[...new Set(params.getAll('tags').flatMap(v=>v.split(',')))].filter(id=>allowedTags.has(id));
    return {area,direction,tags};
  }
  function writeFilters(params,state){
    ['area','direction','tags','topics','exclude','match'].forEach(key=>params.delete(key));
    if(state.area!=='all')params.set('area',state.area);
    if(state.direction!=='all')params.set('direction',state.direction);
    if(state.tags.length)params.set('tags',[...state.tags].sort().join(','));
    return params;
  }
  function matchesClassification(classification,state){
    const ids=tagIds(classification);
    return (state.area==='all'||classification.area===state.area)&&
      (state.direction==='all'||classification.direction===state.direction)&&
      state.tags.every(id=>ids.includes(id));
  }
  function toggleTag(selected,id){return selected.includes(id)?selected.filter(v=>v!==id):[...selected,id];}
  return {tagOptions,tagIds,readFilters,writeFilters,matchesClassification,toggleTag};
});
