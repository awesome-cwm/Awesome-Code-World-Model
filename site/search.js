/* Flat topics: the website matches the intersection of all selected topics. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.CWM_SEARCH=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function readTopics(params,topics){
    const allowed=new Set(topics.map(t=>t.id));
    return [...new Set(params.getAll('topics').flatMap(v=>v.split(',')))].filter(id=>allowed.has(id));
  }
  function writeTopics(params,selected){
    ['topics','area','direction','tags','exclude','match'].forEach(key=>params.delete(key));
    if(selected.length)params.set('topics',[...new Set(selected)].sort().join(','));
    return params;
  }
  function matchesTopics(topics,selected){return selected.every(id=>topics.includes(id));}
  function toggleTopic(selected,id){return selected.includes(id)?selected.filter(v=>v!==id):[...selected,id];}
  return {readTopics,writeTopics,matchesTopics,toggleTopic};
});
