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

function readSingleFileAndApply(fn, e) {
  var file = e.target.files[0];
  if (!file) {
    return;
  }
  var reader = new FileReader();
  reader.onload = function(e) {
    var contents = e.target.result;
    fn(contents);
  };
  reader.readAsText(file);
}


function csvJSON(csv){
    var separator = ",";
    var lines=csv.replace("\r","").split("\n");
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
  return result; //JavaScript object
  //return JSON.stringify(result); //JSON
}

function JSONToDict(JSONList, key){
    var dict = {};
    for( var i = 0; i < JSONList.length; i++){
        var jsonObj = JSONList[i];
        dict[jsonObj[key]] = jsonObj;
    }
    return dict;
}

function fillrow(studentsDict, row){
    var sid = row.getElementsByTagName("td")[1].innerText
    var calif = 50;
    if(sid in studentsDict){
	    calif = studentsDict[sid]["Total"];
	    if(calif < 55){
	    calif = 55
	    }
	    if(calif > 65 && calif < 70){
            calif = 65
        }
    }
    row.getElementsByTagName("td")[4].getElementsByTagName("input")[0].value = calif;
}
function printRow(msg, row){
    var sid =  row.getElementsByTagName("td")[1].innerText;
    console.log(msg + sid);
}
function iterateTable(tbl, fnrow){
    for(var i = 1; i<tbl.rows.length;i++){
        fnrow(tbl.rows[i]);
    }
}

function main(tableToFill, csvContent){
    var sdict = JSONToDict(csvJSON(csvContent), 'Matricula');
    console.log(sdict);
    iterateTable(tableToFill, partial(fillrow, sdict));
}


var baseFrame =  document.getElementsByTagName("frameset")[1].getElementsByTagName("frame")[1];
var baseForm = baseFrame.contentDocument.getElementsByTagName("form")[0]
var tble = baseForm.getElementsByClassName("TablaLink")[0];
var input = document.createElement("input");
input.type = "file";
input.id = "file-input";
baseForm.appendChild(input)

baseFrame.contentDocument.getElementById('file-input').addEventListener('change', partial(readSingleFileAndApply, partial(main, tble)), false);
