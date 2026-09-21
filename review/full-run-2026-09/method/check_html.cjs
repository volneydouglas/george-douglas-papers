const fs=require('fs');
const vm=require('vm');
const cases=JSON.parse(fs.readFileSync('tmp/george_douglas/revision/html-filter-cases.json','utf8'));
for(const c of cases){
  const elements=c.texts.map(textContent=>({textContent,hidden:false}));
  let callback;
  const q={value:'',addEventListener(event,fn){if(event!=='input')throw new Error(event);callback=fn;}};
  const count={textContent:''};
  const document={querySelectorAll(selector){if(selector!==c.selector)throw new Error(selector);return elements;},getElementById(id){if(id==='q')return q;if(id==='count')return count;throw new Error(id);}};
  vm.runInNewContext(c.script,{document});
  for(const query of ['', '05-014', 'DOUGLAS', 'no-such-text-1234567890', '']){
    q.value=query;callback();
    const expected=c.texts.filter(t=>t.toLocaleLowerCase().includes(query.toLocaleLowerCase())).length;
    const actual=elements.filter(e=>!e.hidden).length;
    if(actual!==expected||!count.textContent.startsWith(actual+' of '))throw new Error(c.name+' filter failed '+query);
  }
  console.log(c.name+': filtering, case folding, zero results and reset passed for '+elements.length+' entries');
}
