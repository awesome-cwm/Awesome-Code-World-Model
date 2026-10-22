/* 复合标签索引：无 DOM 依赖，浏览器与 Node 验证使用同一份逻辑。 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CWM_SEARCH = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function topicsFor(paper, topics) {
    const valid = new Set(topics.map(t => t.id));
    // 显式编辑过的标签优先；没有逐篇标签时，仅映射已有目录元数据。
    if (Array.isArray(paper.topics)) return [...new Set(paper.topics)].filter(id => valid.has(id));
    const d = paper.dimensions || {};
    const fields = {
      categories: [paper.category, ...(paper.cross_categories || [])],
      code_roles: d.code_role || [], dynamics: d.dynamics || [],
      representations: d.representation || [], interactions: d.interaction || [],
      collections: paper.collections || []
    };
    return topics.filter(topic => {
      const rules = topic.rules || {};
      return (rules.benchmark && (paper.benchmarks || []).length > 0) ||
        Object.entries(fields).some(([key, values]) => (rules[key] || []).some(v => values.includes(v)));
    }).map(t => t.id);
  }
  function readTopics(params, topics) {
    const valid = new Set(topics.map(t => t.id));
    return {include:[...new Set(params.getAll('topics').flatMap(v=>v.split(',')))].filter(id=>valid.has(id))};
  }
  function writeTopics(params, state) {
    ['topics', 'exclude', 'match'].forEach(key => params.delete(key));
    if (state.include.length) params.set('topics', [...state.include].sort().join(','));
    return params;
  }
  function matchesTopics(ids, state) {
    return state.include.every(id=>ids.includes(id));
  }
  function toggleTopic(selected, id) {
    return selected.includes(id)?selected.filter(v=>v!==id):[...selected,id];
  }
  return {topicsFor, readTopics, writeTopics, matchesTopics, toggleTopic};
});
