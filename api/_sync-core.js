/* The merge rules of the shared test world, used by the server (api/world.js)
 * and, as an identical copy between the same two markers, by the page
 * (prototype/shelfcall-all-roles.html). tests/sync-core.test.js fails if the
 * two copies ever differ. Files in api/ that start with "_" are not routes.
 */
/* ==== sync-core:begin ==================================================== */
var SyncCore = (function(){
  /* Changes travel as a list of operations on paths, not as whole records.
     A request approved by the admin while a bookshop marks it "seen" is two
     edits to two different fields, and both survive. Only two edits to the
     very same field collide, and then the later one wins.

     A path is a list of steps. A step is a key in an object, or {k, v}: the
     element of a list whose field k (id, or no for a shop's part of an order)
     equals v. An operation is one of
       { p: path, v: value }   set the value there (or add the element)
       { p: path, d: 1 }       remove it
       { p: path, add: item }  a list of records without ids (the ledger, a
                               shop's reviews): add one, if it is not there
       { p: path, rem: json }  ... or take one out
     An added element carries i, its position, so a review put at the top
     with unshift is at the top on every phone, not only on the one that
     wrote it.                                                              */

  function isMap(x){ return x !== null && typeof x === 'object' && !Array.isArray(x) }
  function same(a, b){ return JSON.stringify(a) === JSON.stringify(b) }

  /* the field that names the elements of a list, if every element has one */
  function idField(list){
    if (!list.length) return null;
    var fields = ['id', 'no'];
    for (var i = 0; i < fields.length; i++){
      var f = fields[i], all = true;
      for (var j = 0; j < list.length; j++){
        if (!isMap(list[j]) || list[j][f] === undefined || list[j][f] === null){ all = false; break; }
      }
      if (all) return f;
    }
    return null;
  }

  function diff(a, b){
    var ops = [];
    walk(a, b, [], ops);
    return ops;
  }
  function walk(a, b, path, ops){
    if (same(a, b)) return;
    if (isMap(a) && isMap(b)){
      Object.keys(b).forEach(function(k){
        if (!(k in a)) ops.push({ p: path.concat([k]), v: b[k] });
        else walk(a[k], b[k], path.concat([k]), ops);
      });
      Object.keys(a).forEach(function(k){
        if (!(k in b)) ops.push({ p: path.concat([k]), d: 1 });
      });
      return;
    }
    if (Array.isArray(a) && Array.isArray(b)){
      var kf = idField(a.concat(b));
      if (kf){
        var inA = {}, inB = {};
        a.forEach(function(x){ inA[JSON.stringify(x[kf])] = x });
        b.forEach(function(x){
          var key = JSON.stringify(x[kf]), step = { k: kf, v: x[kf] };
          inB[key] = 1;
          if (!(key in inA)) ops.push({ p: path.concat([step]), v: x, i: b.indexOf(x) });
          else walk(inA[key], x, path.concat([step]), ops);
        });
        a.forEach(function(x){
          if (!inB[JSON.stringify(x[kf])]) ops.push({ p: path.concat([{ k: kf, v: x[kf] }]), d: 1 });
        });
        return;
      }
      if (a.concat(b).every(isMap)){
        var setA = {}, setB = {};
        a.forEach(function(x){ setA[JSON.stringify(x)] = 1 });
        b.forEach(function(x, n){
          var s = JSON.stringify(x); setB[s] = 1;
          if (!setA[s]) ops.push({ p: path, add: x, i: n });
        });
        a.forEach(function(x){
          var s = JSON.stringify(x);
          if (!setB[s]) ops.push({ p: path, rem: s });
        });
        return;
      }
    }
    ops.push({ p: path, v: b });
  }

  function indexOf(list, step){
    for (var i = 0; i < list.length; i++){
      if (isMap(list[i]) && same(list[i][step.k], step.v)) return i;
    }
    return -1;
  }

  function insertAt(list, item, i){
    if (typeof i === 'number' && i >= 0 && i < list.length) list.splice(i, 0, item);
    else list.push(item);
  }

  /* Lay operations on a copy of a world. An operation whose record is gone
     (deleted on another phone) is dropped rather than bringing it back. */
  function apply(world, ops){
    var w = JSON.parse(JSON.stringify(world || {}));
    (ops || []).forEach(function(op){ applyOne(w, op) });
    return w;
  }
  function applyOne(root, op){
    var p = op && op.p;
    if (!Array.isArray(p) || !p.length) return;
    var isLog = ('add' in op) || ('rem' in op);
    var stop = isLog ? p.length : p.length - 1;
    var cur = root;
    for (var i = 0; i < stop; i++){
      var step = p[i], next;
      if (isMap(step)){
        if (!Array.isArray(cur)) return;
        var at = indexOf(cur, step);
        if (at < 0) return;
        next = cur[at];
      } else {
        if (!isMap(cur)) return;
        next = cur[step];
        if (next !== undefined && next !== null && typeof next !== 'object') return;
        if (next === undefined || next === null){
          var follow = p[i + 1];
          next = (isLog && i === stop - 1) || isMap(follow) ? [] : {};
          cur[step] = next;
        }
      }
      cur = next;
    }
    if (isLog){
      if (!Array.isArray(cur)) return;
      if ('add' in op){
        var s = JSON.stringify(op.add), have = false;
        for (var a = 0; a < cur.length; a++) if (JSON.stringify(cur[a]) === s){ have = true; break; }
        if (!have) insertAt(cur, op.add, op.i);
      } else {
        for (var r = 0; r < cur.length; r++) if (JSON.stringify(cur[r]) === op.rem){ cur.splice(r, 1); break; }
      }
      return;
    }
    var last = p[p.length - 1];
    if (isMap(last)){
      if (!Array.isArray(cur)) return;
      var j = indexOf(cur, last);
      if (op.d){ if (j >= 0) cur.splice(j, 1); }
      else if (j >= 0) cur[j] = op.v;
      else insertAt(cur, op.v, op.i);
    } else {
      if (!isMap(cur)) return;
      if (op.d) delete cur[last];
      else cur[last] = op.v;
    }
  }

  return { diff: diff, apply: apply, isMap: isMap };
})();
/* ==== sync-core:end ====================================================== */

if (typeof module !== 'undefined' && module.exports) module.exports = SyncCore;
