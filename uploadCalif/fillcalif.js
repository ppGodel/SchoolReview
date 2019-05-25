function partial(fn /*, args...*/) {
    // A reference to the Array#slice method.
    var slice = Array.prototype.slice;
    // Convert arguments object to an array, removing the first argument.
    var args = slice.call(arguments, 1);

    return function() {
      // Invoke the originally-specified function, passing in all originally-
      // specified arguments, followed by any just-specified arguments.
      return fn.apply(this, args.concat(slice.call(arguments, 0)));
    };
}
function csvJSON(csv){
    var separator = ","
    var lines=csv.split("\n");
    var result = [];
    var headers=lines[0].split(separator);
    for(var i=1;i<lines.length;i++){
	var obj = {};
	var currentline=lines[i].split(separator);
	for(var j=0;j<headers.length;j++){
	    obj[headers[j]] = currentline[j];
	}
	result.push(obj);
  }
  //return result; //JavaScript object
  return JSON.stringify(result); //JSON
}
function fillrow(studentsDict, row){
    var sid =  row.getElementsByTagName("td")[1].innerText
    calif=0
    if(sid in studentDict){
	calif = studentsDict[sid]
    }
    row.getElementsByTagName("td")[5].getElementsByTagName("input")[0].value = calif
}
function printRow(msg, row){
    var sid =  row.getElementsByTagName("td")[1].innerText
    console.log(msg + sid)
}
function iterateTable(tbl, fnrow){
    for(var i=1; i<tbl.rows.length;i++){
    fnrow(tbl.rows[i])
    }
}
function openJsonFile(path){
   return var json = require(path); 
}

var sdict = openJsonFile('')
var tble = document.getElementsByTagName("frameset")[1].getElementsByTagName("frame")[1].contentDocument.getElementsByTagName("form")[0].getElementsByClassName("TablaLink")[0]

iterateTable(tble, partial(fillrow, sdict))
